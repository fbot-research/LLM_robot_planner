# Tools for ROS2 operations
from fastapi import logger


tools = [
    {
        "name": "list_topics",
        "description": "List all available ROS topics.",
        "parameters": {}
    },
    {
        "name": "publish",
        "description": "Publish a message to a ROS topic. Useful for sending commands or data to the robot.",
        "parameters": {
            "topic": "string, the ROS topic to publish to (e.g., '/cmd_vel').",
            "message": "string, the message to publish (e.g., 'linear: 0.5, angular: 0.0')."
        }
    },
    {
        "name": "call_service",
        "description": "Call a ROS service to perform an action or get information. Useful for interacting with ROS services that control robot behavior or query state.",
        "parameters": {
            "service": "string, the ROS service to call (e.g., '/move_base/move').",
            "request": "string, the request message to send to the service (e.g., 'target_pose: {x: 1.0, y: 0.  0}')."
        }
    }
]

implementation = {
    "list_topics": lambda: list_ros_topics(),
    "publish": lambda topic, message: publish_ros_message(topic, message),
    "call_service": lambda service, request: call_ros_service(service, request),
}

def call_ros_command(command: str) -> str:
    """Execute a ROS command and return its output as a string."""
    import subprocess

    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        logger.error(f"ROS command failed: {e.stderr.decode('utf-8')}")
        return f"Error calling ROS command: {e.stderr.decode('utf-8')}"

def list_ros_topics():
    """List all available ROS topics."""
    return call_ros_command("ros2 topic list")

def publish_ros_message(topic: str, message: str):
    """Publish a message to a ROS topic."""
    command = f"ros2 topic pub {topic} {message}"
    return call_ros_command(command)

def call_ros_service(service: str, request: str):
    """Call a ROS service with a request message."""
    command = f"ros2 service call {service} {request}"
    return call_ros_command(command)