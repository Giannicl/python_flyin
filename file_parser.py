from area import StartZone, EndZone, Connection, SpecialZone


def parser(filename: str) -> list[StartZone | EndZone | Connection | SpecialZone]:
    graph = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "hub" in line:
                

    return


if __name__ == "__main__":
    parser("./maps/easy/01_linear_path.txt")
