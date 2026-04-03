from area import Zone, Connection, Graph


def parser(filename: str) -> list[Zone | Connection]:

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "start_hub" in line:
                parts = split(lines, " ")
                color = split(parts[3], "=")
                start_zone = Zone("start", parts[2], parts[3], color[1])

    return Graph


if __name__ == "__main__":
    parser("./maps/easy/01_linear_path.txt")
