import matplotlib.pyplot as plt
from simulator.draftsimulator import DraftSimulator

if __name__ == "__main__":
    print("Hello Cat-An!")
    sim = DraftSimulator()
    for i in range(8):
        sim.step()
        # sim.render(title=f"After turn #{i+1}")
    sim.render(title=f"After draft")
    plt.show()