import matplotlib.pyplot as plt
from simulator.draftsimulator import DraftSimulator
from collections import defaultdict

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
    for trial in range(100):
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