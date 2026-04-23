from pydantic import BaseModel, Field
from tool_registry import tool
import rclpy
from geometry_msgs.msg import PoseStamped, Quaternion
from nav2_simple_commander.robot_navigator import BasicNavigator

class NavigateToSchema(BaseModel):
    x: float = Field(..., description="Target x coordinate")
    y: float = Field(..., description="Target y coordinate")
    z: float = Field(..., description="Target z coordinate")
    orientation: list[float] = Field(..., description="Quaternion [x, y, z, w]")

@tool(args_schema=NavigateToSchema)
def navigate_to(x: float, y: float, z: float, orientation: list[float]):
    """Navigate the robot to a specified pose using Nav2."""
    rclpy.init()
    navigator = BasicNavigator()
    navigator.waitUntilNav2Active()
    
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = x
    goal_pose.pose.position.y = y
    goal_pose.pose.position.z = z
    goal_pose.pose.orientation = Quaternion(
        x=orientation[0],
        y=orientation[1],
        z=orientation[2],
        w=orientation[3]
    )
    
    navigator.goToPose(goal_pose)
    
    while not navigator.isTaskComplete():
        pass
    
    result = navigator.getResult()
    navigator.lifecycleShutdown()
    rclpy.shutdown()
    
    if result == navigator.SUCCEEDED:
        return {"status": "success", '__control__': 'done'}
    else:
        return {"status": f"failed: {result}", '__control__': 'error'}
