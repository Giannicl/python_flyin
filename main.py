from simulation import Simulation


def main() -> None:
    try:
        sim = Simulation("./maps/hard/01_maze_nightmare.txt")
        sim.run()
    except ValueError as e:
        print(f"Error: {e}")
    # except Exception as e:
    #   print(f"Unknow error: {e}")


if __name__ == "__main__":
    main()
