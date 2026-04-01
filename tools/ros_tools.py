from pydantic import BaseModel, Field
from tool_registry import tool
from subprocess import run

class ROSCommandSchema(BaseModel):
    parameters: dict = Field({}, description="Parameters for the ROS command, if applicable.")

@tool(args_schema=ROSCommandSchema)
def list_topics(parameters: dict):
    run('ros2 topic list', shell=True, check=True)

@tool(args_schema=ROSCommandSchema)
def echo_topic(parameters: dict):
    topic = parameters.get("topic")
    if not topic:
        return "Error: 'topic' parameter is required."
    run(f'ros2 topic echo {topic} --once', shell=True, check=True)

@tool(args_schema=ROSCommandSchema)
def publish(parameters: dict):
    topic = parameters.get("topic")
    message = parameters.get("message")
    if not topic or not message:
        return "Error: 'topic' and 'message' parameters are required."
    run(f'ros2 topic pub {topic} "{message}"', shell=True, check=True)

@tool(args_schema=ROSCommandSchema)
def call_service(parameters: dict):
    service = parameters.get("service")
    request = parameters.get("request")
    if not service or not request:
        return "Error: 'service' and 'request' parameters are required."
    run(f'ros2 service call {service} "{request}"', shell=True, check=True)

