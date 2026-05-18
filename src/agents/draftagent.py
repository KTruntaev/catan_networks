import random

from networkx.classes.graph import Graph

from agents.agent import Agent
from catan_nets.network import is_node_settleable, is_edge_roadable_draft
from catan_nets.state import BoardState
from utils.action import Action, PlaceSettlement, PlaceRoad, SimResponse

class RandomAgent(Agent):
    def __init__(self, id: int = random.randint(1,777), debug=False):
        super().__init__(id=id, debug=debug)
        self.settlements: set[int] = set()
        self.roads: set[tuple[int,int]] = set()

    def act(self, bstate: BoardState) -> list[Action]:
        self.debug_print(bstate.network)
        network = bstate.network
        turn = bstate.turn

        node, edge = None, None
        # this sample draft agent simply randomly picks a node + edge to place
        while True:
            rand_node_idx = random.randint(0, network.number_of_nodes()-1)

            # find a settleable node
            if not is_node_settleable(network, rand_node_idx):
                continue

            # pick from incident edges
            rand_edge = random.choice(list(network.edges(rand_node_idx)))
            if network.edges[rand_edge]["owner"] != -1:
                # no need to check adjacency as we only pick from incident edges
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


class DeterministicAgent(Agent):
    def __init__(self, id: int = random.randint(1, 777), debug=False, moves: list[Action] = []):
        # pass
        super().__init__(id=id, debug=debug)
        self.moves = moves
        self.curr_move_i = 0

    def act(self, network: Graph) -> list[Action]:
        if self.curr_move_i >= len(self.moves):
            raise IndexError (f"agent {self.id} has run out of moves")
        move = self.moves[self.curr_move_i]
        self.curr_move_i += 1
        return [move]

    def observe(self, network: Graph, responses: list[SimResponse]):
        pass
