from networkx.classes import Graph
import matplotlib.pyplot as plt

from agents.agent import Agent
from agents.draftagent import DraftAgent
from utils.action import Action, PlaceSettlement, PlaceRoad, SimResponse
from catan_nets.network import generate_beginner_board_graph
from catan_nets.visualization import draw_game_state

class DraftSimulator():
    def __init__(self):
        self.agents: dict[int, Agent] = {}
        for i in range(4):
            self.agents[i] = DraftAgent(i)
        self.curr_agent_idx = 0
        self.dir = 1

        self.network, self.hex_centers, self.tile_data = generate_beginner_board_graph()

    def execute_action(self, agent: Agent, action: Action) -> SimResponse:
        match action:
            case PlaceSettlement(node=n):
                if self.network.nodes[n]["owner"] == -1:
                    self.network.nodes[n]["owner"] = agent.id
                    return SimResponse(action=action, ack=True)
                else:
                    return SimResponse(action=action, ack=False)
            case PlaceRoad(edge=e):
                if self.network.edges[e]["owner"] == -1:
                    self.network.edges[e]["owner"] = agent.id
                    return SimResponse(action=action, ack=True)
                else:
                    return SimResponse(action=action, ack=False)
            case _:
                raise ValueError(f"undefined action: {action}")

    def step(self):
        # print(self.curr_agent_idx)
        self.debug_print(self.curr_agent_idx)
        curr_agent = self.agents[self.curr_agent_idx]
        agent_acts = curr_agent.act(network=self.network)

        if agent_acts is not None:
            responses: list[SimResponse] = []
            for a_act in agent_acts:
                responses.append(self.execute_action(agent = curr_agent, action = a_act))
            curr_agent.observe(network=self.network, responses=responses)

        # 1 2 3 4 4 3 2 1
        self.curr_agent_idx += self.dir
        if self.curr_agent_idx == 4:
            self.dir *= -1
            self.curr_agent_idx = 3


    def render(self, title="Game State", ax=None):
        return draw_game_state(self.network, self.hex_centers, self.tile_data,
                               title=title, ax=ax)

    def debug_print(self, input: str):
        print(f"[SIM]: {input}")

if __name__ == "__main__":
    print("Hello Cat-An!")
    sim = DraftSimulator()
    for i in range(8):
        sim.step()
        # sim.render(title=f"After turn #{i+1}")
    sim.render(title=f"After draft")
    plt.show()

