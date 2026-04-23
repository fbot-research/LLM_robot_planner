from pydantic import BaseModel, Field
from tool_registry import tool
import rclpy
from rclpy.node import Node
import json
import importlib
import time

class ListTopicsSchema(BaseModel):
    pass

class EchoTopicSchema(BaseModel):
    topic: str = Field(..., description="The ROS topic to echo")

class PublishSchema(BaseModel):
    topic: str = Field(..., description="The ROS topic to publish to")
    message: str = Field(..., description="The message to publish")

class CallServiceSchema(BaseModel):
    service: str = Field(..., description="The ROS service to call")
    request: str = Field(..., description="The request payload to send to the service")


@tool(args_schema=ListTopicsSchema)
def list_topics():
    """List all active ROS topics.
    
    Queries the ROS2 graph to display all currently active topics.
    This is useful for discovering available data streams and topic names
    that can be echoed or subscribed to.
    
    Returns:
        dict: Status and list of topics with their message types.
    """
    try:
        rclpy.init()
        node = rclpy.create_node('topic_lister')
        
        topic_names_and_types = node.get_topic_names_and_types()
        topics_list = []
        for name, types in topic_names_and_types:
            topics_list.append({"name": name, "type": types[0] if types else "unknown"})
        
        node.destroy_node()
        rclpy.shutdown()
        
        return {"status": "success", "topics": topics_list, "__control__": "done"}
    except Exception as e:
        try:
            rclpy.shutdown()
        except:
            pass
        return {"status": f"Error listing topics: {str(e)}", "__control__": "error"}

@tool(args_schema=EchoTopicSchema)
def echo_topic(topic: str):
    """Echo the messages on a specified ROS topic.
    
    Subscribes to a topic and receives a single message from that topic.
    This is useful for inspecting the data format and content of messages being
    published on a specific topic without requiring a long-running subscription.
    
    Args:
        topic: The name of the ROS topic to echo from.
    
    Returns:
        dict: Status and message content if successful.
    """
    if not topic:
        return {"status": "Error: 'topic' parameter is required.", "__control__": "error"}
    try:
        rclpy.init()
        node = rclpy.create_node('topic_echo')
        
        # Get topic type
        topic_type = get_topic_type(node, topic)
        if not topic_type:
            return {"status": f"Error: Could not determine type for topic '{topic}'", "__control__": "error"}
        
        # Import message class
        msg_class = import_message_class(topic_type)
        if not msg_class:
            return {"status": f"Error: Could not import message type '{topic_type}'", "__control__": "error"}
        
        # Subscribe and get one message
        message_received = [None]
        
        def callback(msg):
            message_received[0] = msg
        
        subscription = node.create_subscription(msg_class, topic, callback, 10)
        
        # Wait for message with timeout
        start_time = time.time()
        timeout = 5.0  # 5 second timeout
        while message_received[0] is None and (time.time() - start_time) < timeout:
            rclpy.spin_once(node, timeout_sec=0.1)
        
        node.destroy_subscription(subscription)
        node.destroy_node()
        rclpy.shutdown()
        
        if message_received[0] is None:
            return {"status": f"Error: No message received on '{topic}' within timeout", "__control__": "error"}
        
        msg_str = str(message_received[0])
        return {"status": "success", "message": msg_str, "__control__": "done"}
    except Exception as e:
        try:
            rclpy.shutdown()
        except:
            pass
        return {"status": f"Error echoing topic: {str(e)}", "__control__": "error"}

@tool(args_schema=PublishSchema)
def publish(topic: str, message: str):
    """Publish a message of any type to a specified ROS topic.
    
    Automatically discovers the topic's message type and publishes data accordingly.
    The message parameter can be:
    - Plain text (for String topics)
    - JSON object (for structured message types, e.g. {"x": 1.0, "y": 2.0})
    
    Args:
        topic: The name of the ROS topic to publish to.
        message: The message content (string or JSON).
    
    Returns:
        dict: Status of the operation with error details if applicable.
    """
    if not topic or not message:
        return {"status": "Error: 'topic' and 'message' parameters are required.", "__control__": "error"}
    
    try:
        rclpy.init()
        node = rclpy.create_node('dynamic_publisher')
        
        # Get topic type
        topic_type = get_topic_type(node, topic)
        if not topic_type:
            return {"status": f"Error: Could not determine type for topic '{topic}'", "__control__": "error"}
        
        # Dynamically import the message class
        msg_class = import_message_class(topic_type)
        if not msg_class:
            return {"status": f"Error: Could not import message type '{topic_type}'", "__control__": "error"}
        
        # Create publisher and message
        publisher = node.create_publisher(msg_class, topic, 10)
        msg_instance = create_message_instance(msg_class, message)
        
        if msg_instance is None:
            return {"status": f"Error: Could not create message instance for type '{topic_type}'", "__control__": "error"}
        
        # Publish
        publisher.publish(msg_instance)
        time.sleep(0.1)
        
        node.destroy_node()
        rclpy.shutdown()
        
        return {"status": "success", "__control__": "done"}
    
    except Exception as e:
        try:
            rclpy.shutdown()
        except:
            pass
        return {"status": f"Error publishing to topic: {str(e)}", "__control__": "error"}


def get_topic_type(node: Node, topic: str) -> str:
    """Query the topic type from the ROS graph."""
    try:
        topic_names_and_types = node.get_topic_names_and_types()
        for name, types in topic_names_and_types:
            if name == topic and types:
                return types[0]
        return None
    except Exception as e:
        print(f"Error getting topic type: {e}")
        return None


def import_message_class(msg_type: str):
    """Dynamically import a ROS message class.
    
    Args:
        msg_type: Message type string (e.g. "std_msgs/String")
    
    Returns:
        The message class or None if import fails.
    """
    try:
        # Parse message type: "package/ClassName"
        parts = msg_type.split('/')
        if len(parts) != 2:
            return None
        
        package, class_name = parts
        # Convert to snake_case for module name
        module_name = ''.join(['_' + c.lower() if c.isupper() else c for c in class_name]).lstrip('_')
        
        module = importlib.import_module(f'{package}.msg')
        return getattr(module, class_name, None)
    except Exception as e:
        print(f"Error importing message class: {e}")
        return None


def create_message_instance(msg_class, data: str):
    """Create and populate a message instance.
    
    Args:
        msg_class: The ROS message class
        data: Data as a string (JSON for structured types, plain text for String types)
    
    Returns:
        A populated message instance or None if creation fails.
    """
    try:
        msg = msg_class()
        
        # Try to parse as JSON first
        try:
            data_dict = json.loads(data)
            # Populate message fields from JSON
            for key, value in data_dict.items():
                if hasattr(msg, key):
                    setattr(msg, key, value)
        except json.JSONDecodeError:
            # If not JSON, treat as plain text
            if hasattr(msg, 'data'):
                msg.data = data
            else:
                # Try to set first string field
                for field_name in msg.get_fields_and_field_types():
                    setattr(msg, field_name, data)
                    break
        
        return msg
    except Exception as e:
        print(f"Error creating message instance: {e}")
        return None


def import_service_class(srv_type: str):
    """Dynamically import a ROS service class.
    
    Args:
        srv_type: Service type string (e.g. "std_srvs/Trigger")
    
    Returns:
        The service class or None if import fails.
    """
    try:
        # Parse service type: "package/ServiceName"
        parts = srv_type.split('/')
        if len(parts) != 2:
            return None
        
        package, class_name = parts
        module = importlib.import_module(f'{package}.srv')
        return getattr(module, class_name, None)
    except Exception as e:
        print(f"Error importing service class: {e}")
        return None

@tool(args_schema=CallServiceSchema)
def call_service(service: str, request: str):
    """Call a ROS service with a request payload.
    
    Calls a ROS service endpoint with the specified request data using rclpy.
    This is useful for triggering service procedures, issuing commands, or 
    requesting computations from service servers. The request should be formatted
    as JSON matching the service request message structure.
    
    Args:
        service: The name of the ROS service to call.
        request: The request payload as a JSON string.
    
    Returns:
        dict: Status and response if successful.
    """
    if not service or not request:
        return {"status": "Error: 'service' and 'request' parameters are required.", "__control__": "error"}
    try:
        rclpy.init()
        node = rclpy.create_node('service_caller')
        
        # Get service type
        service_names_and_types = node.get_service_names_and_types()
        service_type = None
        for name, types in service_names_and_types:
            if name == service and types:
                service_type = types[0]
                break
        
        if not service_type:
            return {"status": f"Error: Service '{service}' not found", "__control__": "error"}
        
        # Import service class
        srv_class = import_service_class(service_type)
        if not srv_class:
            return {"status": f"Error: Could not import service type '{service_type}'", "__control__": "error"}
        
        # Create client and prepare request
        client = node.create_client(srv_class, service)
        
        # Wait for service to be available
        if not client.wait_for_service(timeout_sec=5.0):
            return {"status": f"Error: Service '{service}' not available", "__control__": "error"}
        
        # Parse request and populate service request
        request_obj = srv_class.Request()
        try:
            request_dict = json.loads(request)
            for key, value in request_dict.items():
                if hasattr(request_obj, key):
                    setattr(request_obj, key, value)
        except json.JSONDecodeError:
            return {"status": f"Error: Invalid JSON in request", "__control__": "error"}
        
        # Call service
        future = client.call_async(request_obj)
        
        # Wait for response with timeout
        start_time = time.time()
        timeout = 5.0
        while not future.done() and (time.time() - start_time) < timeout:
            rclpy.spin_once(node, timeout_sec=0.1)
        
        if not future.done():
            return {"status": f"Error: Service call timeout", "__control__": "error"}
        
        response = future.result()
        node.destroy_node()
        rclpy.shutdown()
        
        return {"status": "success", "response": str(response), "__control__": "done"}
    except Exception as e:
        try:
            rclpy.shutdown()
        except:
            pass
        return {"status": f"Error calling service: {str(e)}", "__control__": "error"}

