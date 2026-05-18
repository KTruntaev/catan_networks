from attr import dataclass
from networkx.classes import Graph

@dataclass
class BoardState:
    """
        global state of the board
    """
    network: Graph
    turn: int