from simulation import Simulation
from visualizer import Visualizer
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Fly-in Drone Simulation")
    parser.add_argument(
        "map_file",
        type=str,
        help="Path to the map file",
    )
    parser.add_argument(
        "--visual",
        action="store_true",
        help="Show graphical visualization after the terminal simulation",
    )
    parser.add_argument(
        "--capacity-info", action="store_true", help="Show capacity usage per turn"
    )
    args = parser.parse_args()

    try:
        sim: Simulation = Simulation(args.map_file)
        sim.capacity_info_enabled = args.capacity_info
        sim.run()
        print(f"Completed in {sim.turns} turns")
        if args.visual:
            visualizer: Visualizer = Visualizer(sim.graph, sim.frames)
            visualizer.run()
    except ValueError as e:
        print(f"Invalid input: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except Exception as e:
        print(f"Unknow error: {e}")


if __name__ == "__main__":
    main()
