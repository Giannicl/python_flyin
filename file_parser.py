from area import Zone, Connection, Graph
from typing import Dict, List


def zone_instantiator(line: str) -> Dict:
    elements: Dict = {}
    parts: List = line.split(" ", 4)
    elements["name"] = parts[1]
    elements["xaxis"] = int(parts[2])
    elements["yaxis"] = int(parts[3])
    if "[" in line:
        meta_data: List = parts[4][1:-1].split(" ")
        for item in meta_data:
            parts: list = item.split("=")
            name: str = parts[0]
            data: int | str = int(parts[1]) if parts[1].isdigit() else parts[1]
            elements[name] = data
    return elements


def connection_instatiator(line: str, id: int) -> Dict:
    elements: Dict = {}
    parts: List = line.split(" ")
    elements["id"] = id
    zone1, zone2 = parts[1].split("-")
    elements["zone1"] = zone1
    elements["zone2"] = zone2
    return elements


def parser(filename: str) -> list[Zone | Connection]:
    graph: Graph = Graph()
    id: int = 0
    with open(filename, "r") as file:
        for line in file:
            line: List = line.strip()
            if not line or line.startswith("#"):
                continue
            if "nb_drones" in line:
                graph.nb_drones = int(line.split(" ")[1])
            if "hub" in line.split(" ")[0]:
                zone_elements: Dict = zone_instantiator(line)
                zone: Zone = Zone(
                    zone_elements.get("name"),
                    zone_elements.get("xaxis"),
                    zone_elements.get("yaxis"),
                    zone_type=zone_elements.get("zone_type", "normal"),
                    color=zone_elements.get("color", "none"),
                    max_drones=zone_elements.get("max_drones", 1),
                )
                graph.create_graph(zone)
            if "connection" in line.split(" ")[0]:
                id += 1
                connection_elements: Dict = connection_instatiator(line, id)
                name_zone1: str = connection_elements.get("zone1")
                name_zone2: str = connection_elements.get("zone2")
                connection = Connection(
                    connection_elements.get("id"),
                    graph.zones[name_zone1],
                    graph.zones[name_zone2],
                )
                graph.create_graph(connection)
    return graph


if __name__ == "__main__":
    graph = parser("./maps/easy/01_linear_path.txt")
    print(graph.nb_drones)
