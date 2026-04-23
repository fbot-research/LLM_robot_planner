from pydantic import BaseModel, Field
from tool_registry import tool
import rclpy
from moveit_commander import MoveGroupCommander
from geometry_msgs.msg import PoseStamped, Quaternion

class MoveArmSchema(BaseModel):
    x: float = Field(..., description="Target x coordinate in meters")
    y: float = Field(..., description="Target y coordinate in meters")
    z: float = Field(..., description="Target z coordinate in meters")
    orientation: list[float] | None = Field(None, description="Orientation as a quaternion [x, y, z, w]")

@tool(args_schema=MoveArmSchema)
def move_arm(x: float, y: float, z: float, orientation: list[float] | None = None):
    """Move the arm to a specified pose in meters using MoveIt."""
    try:
        rclpy.init()
        move_group = MoveGroupCommander("arm")
        
        # Create target pose
        target_pose = PoseStamped()
        target_pose.header.frame_id = "base_link"
        target_pose.pose.position.x = x
        target_pose.pose.position.y = y
        target_pose.pose.position.z = z
        
        if orientation:
            target_pose.pose.orientation = Quaternion(
                x=orientation[0],
                y=orientation[1],
                z=orientation[2],
                w=orientation[3]
            )
        
        # Set pose target and plan
        move_group.set_pose_target(target_pose)
        plan = move_group.plan()
        
        # Execute plan
        if plan[0]:
            move_group.execute(plan[1], wait=True)
            move_group.stop()
            move_group.clear_pose_targets()
            return {"status": "success", '__control__': 'continue'}
        else:
            return {"status": "failed: planning failed", '__control__': 'error'}
    
    except Exception as e:
        return {"status": f"failed: {str(e)}", '__control__': 'error'}
    finally:
        rclpy.shutdown()
