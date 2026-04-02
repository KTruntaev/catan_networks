import random

from networkx.classes.graph import Graph

from agents.agent import Agent
from utils.action import Action, PlaceSettlement, PlaceRoad, SimResponse


class DraftAgent(Agent):
    def __init__(self, id: int = random.randint(1,777), debug=False):
        super().__init__(id=id)
        self.settlements: set[int] = set()
        self.roads: set[tuple[int,int]] = set()


    def act(self, network: Graph) -> list[Action]:
        node, edge = None, None
        # this sample draft agent simply randomly picks a node + edge to place
        while True:
            rand_node_idx = random.randint(0, network.number_of_nodes()-1)
            if network.nodes[rand_node_idx]["owner"] != -1:
                continue

            rand_edge = random.choice(list(network.edges(rand_node_idx)))
            if network.edges[rand_edge]["owner"] != -1:
                continue

            node = rand_node_idx
            edge = rand_edge
            break
        self.debug_print(f"I want to place a settlement @ {node} and road @ {edge}")
        return [PlaceSettlement(node), PlaceRoad(edge)]

    def observe(self, network: Graph, responses: list[SimResponse]):
        for resp in responses:
            if resp.ack:
                match resp.action:
                    case PlaceSettlement(node=n):
                        self.settlements.add(n)
                    case PlaceRoad(edge=e):
                        self.roads.add(e)


