from pydantic import BaseModel, Field
from tool_registry import tool

class MoveArmSchema(BaseModel):
    x: float = Field(..., description="Target x coordinate in meters")
    y: float = Field(..., description="Target y coordinate in meters")
    z: float = Field(..., description="Target z coordinate in meters")
    orientation: list[float] | None = Field(None, description="Orientation as a quaternion [x, y, z, w]")

@tool(args_schema=MoveArmSchema)
def move_arm(x: float, y: float, z: float, orientation: list[float] | None = None):
    """Move the arm to a specified pose in meters.
    """
    # Aqui você pode implementar a lógica para enviar comandos ROS para mover o braço.
    # Por exemplo, usando ros2 service call ou publicando em um tópico específico.
    print(f"Moving arm to position: x={x}, y={y}, z={z} with orientation {orientation if orientation else 'default'}")
    return {"status": "success", '__control__': 'continue'}
