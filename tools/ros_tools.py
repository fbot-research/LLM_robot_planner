from pydantic import BaseModel, Field
from tool_registry import tool
from subprocess import run

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
    run('ros2 topic list', shell=True, check=True)
    return {"status": "success", "__control__": "done"}

@tool(args_schema=EchoTopicSchema)
def echo_topic(topic: str):
    if not topic:
        return {"status": "Error: 'topic' parameter is required.", "__control__": "error"}
    try:
        run(f'ros2 topic echo {topic} --once', shell=True, check=True)
        return {"status": "success", "__control__": "done"}
    except Exception as e:
        return {"status": f"Error echoing topic: {e}", "__control__": "error"}

@tool(args_schema=PublishSchema)
def publish(topic: str, message: str):
    if not topic or not message:
        return {"status": "Error: 'topic' and 'message' parameters are required.", "__control__": "error"}
    try:
        run(f'ros2 topic pub {topic} "{message}"', shell=True, check=True)
        return {"status": "success", "__control__": "done"}
    except Exception as e:
        return {"status": f"Error publishing to topic: {e}", "__control__": "error"}

@tool(args_schema=CallServiceSchema)
def call_service(service: str, request: str):
    if not service or not request:
        return {"status": "Error: 'service' and 'request' parameters are required.", "__control__": "error"}
    try:
        run(f'ros2 service call {service} "{request}"', shell=True, check=True)
        return {"status": "success", "__control__": "done"}
    except Exception as e:
        return {"status": f"Error calling service: {e}", "__control__": "error"}

