from pydantic import BaseModel, Field
from tool_registry import tool

class NavigateToSchema(BaseModel):
    x: float = Field(..., description="Target x coordinate")
    y: float = Field(..., description="Target y coordinate")
    z: float = Field(..., description="Target z coordinate")
    orientation: list[float] = Field(..., description="Quaternion [x, y, z, w]")

@tool(args_schema=NavigateToSchema)
def navigate_to(x: float, y: float, z: float, orientation: list[float]):
    print(f"Navigating to coordinates: ({x}, {y}, {z}) with orientation (quaternion): {orientation}")
    return {"status": "success", '__control__': 'continue'}
