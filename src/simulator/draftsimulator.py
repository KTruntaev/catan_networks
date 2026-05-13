from collections import defaultdict

from networkx.classes import Graph
import matplotlib.pyplot as plt

from agents.agent import Agent
from agents.draftagent import DraftAgent
from utils.action import Action, PlaceSettlement, PlaceRoad, SimResponse
from catan_nets.network import generate_beginner_board_graph
from catan_nets.visualization import draw_game_state

class DraftSimulator():
    def __init__(self, debug=False, agents: dict[int, Agent] = None, num_agents: int = 4):
        self.debug = debug
        self.num_agents = num_agents
        if agents is None:
            self.agents: dict[int, Agent] = {}
            for i in range(self.num_agents):
                self.agents[i] = DraftAgent(i, debug=self.debug)

        self.curr_agent_idx = 0
        self.dir = 1

        self.network, self.hex_centers, self.tile_data = generate_beginner_board_graph()
        self.action_history: list[tuple[int, Action]] = []

    def execute_action(self, agent: Agent, action: Action) -> SimResponse:
        self.action_history.append((agent.id, action))
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
        if self.curr_agent_idx == self.num_agents:
            self.dir *= -1
            self.curr_agent_idx = 3


    def render(self, title="Game State", ax=None):
        return draw_game_state(self.network, self.hex_centers, self.tile_data,
                               title=title, ax=ax)

    def analyze(self) -> dict[int, dict[str, float]]:
        """
        returns a dict of dicts of sim observations:
         - 'total_pips'
         - 'wood', 'wheat', 'sheep', 'brick', 'ore'

         access via dict[{agent_id}][{obs_key}]
        """
        obs_dict = {agent_idx : defaultdict(int) for agent_idx in self.agents.keys()}

        for k in ['total_pips', 'wood', 'wheat', 'sheep', 'brick', 'ore']:
            weighted_deg_c = dict(self.network.degree(weight=k))
            # kind of wasteful to iterate over ALL nodes but alas
            for node_i, val in weighted_deg_c.items():
                # print(self.network.nodes[node_i], val)
                owner = self.network.nodes[node_i]["owner"]
                if owner != -1:
                    obs_dict[owner][k] += val

        return obs_dict

    def debug_print(self, input: str):
        if self.debug:
            print(f"[SIM]: {input}")

if __name__ == "__main__":
    # print("Hello Cat-An!")
    # sim = DraftSimulator()
    # for i in range(8):
    #     sim.step()
    #     # sim.render(title=f"After turn #{i+1}")
    # sim.render(title=f"After draft")
    # plt.show()


    print("Hello Cat-An!")
    # obs_hist: dict[str, list[float]] = {}
    obs_hist: dict[int, dict[str, list[float]]] = {agent_idx: defaultdict(list[float]) for agent_idx in [0,1,2,3]}
    for trial in range(100000):
        sim = DraftSimulator()
        for i in range(8):
            sim.step()
            # sim.render(title=f"After turn #{i+1}")
        # sim.render(title=f"After draft")
        # plt.show()
        obs = sim.analyze()
        for agent_k, vals in obs.items():
            for val_k, val_val in vals.items():
                obs_hist[agent_k][val_k].append(val_val)
        # print(obs_hist)

    data = []
    for i in range(4):
        data.extend(obs_hist[i]["total_pips"])
    # plt.hist(obs_hist[1]["total_pips"])
    plt.hist(data)
    plt.show()
    print("finished")