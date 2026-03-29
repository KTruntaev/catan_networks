from dataclasses import dataclass
from typing import TypeAlias

@dataclass(frozen=True)
class PlaceSettlement:
    node: int

@dataclass(frozen=True)
class PlaceRoad:
    edge: tuple[int, int]

Action: TypeAlias = PlaceSettlement | PlaceRoad

@dataclass(frozen=True)
class SimResponse:
    action: Action
    ack: bool   # did the sim accept (True) or reject (False) the act