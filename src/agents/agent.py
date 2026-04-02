import random
from abc import ABC, abstractmethod
from argparse import Action

from networkx.classes.graph import Graph

from utils.action import SimResponse


class Agent (ABC):
    """
    Agent base class
    """
    def __init__(self, id: int):
        self.id = id

    @abstractmethod
    def act(self, network: Graph) -> list[Action]:
        """
        agent emits actions for the sim

        Note: currently if an agent issues an invalid action it is ignored by the sim
        """
        pass

    @abstractmethod
    def observe(self, network: Graph, responses: list[SimResponse]):
        """
        agent getting feedback from the sim
        """
        pass

    def debug_print(self, input: str):
        print(f"[{self.id}]: {input}")