from simulation import Simulation
from visualizer import Visualizer


def main() -> None:
    try:
        sim: Simulation = Simulation("./maps/hard/01_maze_nightmare.txt")
        sim.run()
        visualizer: Visualizer = Visualizer(sim.graph, sim.frames)
        visualizer.run()
    except ValueError as e:
        print(f"Error: {e}")
    # except Exception as e:
    #   print(f"Unknow error: {e}")


if __name__ == "__main__":
    main()
