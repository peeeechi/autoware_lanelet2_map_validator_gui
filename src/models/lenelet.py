import typing
from pydantic import BaseModel, RootModel

T = typing.TypeVar('T')

class LaneletPolygon2d(BaseModel):
    x: typing.List[float]
    y: typing.List[float]
    left_bound_id: int
    right_bound_id: int
    lane_id: int


class LaneletPolygon3d(LaneletPolygon2d):
    z: typing.List[float]
