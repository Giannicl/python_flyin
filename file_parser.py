from models import Zone, Connection, Graph
from typing import Dict, List

def initialise_metadata(elements: Dict, meta_data: List[str | int]) -> None:
    for item in meta_data:
        parts: list = item.split("=")
        key = parts[0]
        if key == "zone":
            key: str = "zone_type"
        value: int | str = int(parts[1]) if parts[1].isdigit() else parts[1]
        initialise_zone(elements, key, value)

def initialise_zone(elements: Dict, key: str, value: any) -> None:
    elements[key] = value

def zone_instantiator(line: str) -> Dict:
    elements: Dict = {}
    key: str = ""
    parts: List = line.split(" ", 4)
    for i in range(len(parts)):
        if parts[i] == "start_hub:" or parts[i] == "end_hub:":
            key = "zone_type"
            value = "start" if parts[0] == "start_hub:" else "end"
            initialise_zone(elements, key, value)
        if i == 1:
            key = "name"
            value = parts[1]
            initialise_zone(elements, key, value)
        elif i == 2 and parts[2].isdigit():
            key = "xaxis"
            value = int(parts[2])
            initialise_zone(elements, key, value)
        elif i == 3 and parts[3].isdigit():
            key = "yaxis"
            value = int(parts[3])
            initialise_zone(elements, key, value)
    if "[" in line and "=" in line:
        meta_data: List = parts[4][1:-1].split(" ")
        initialise_metadata(elements, meta_data)
    return elements


def connection_instatiator(line: str) -> Dict:
    elements: Dict = {}
    parts: List = line.split(" ")
    elements["id"] = parts[1]
    zone1, zone2 = parts[1].split("-")
    elements["zone1"] = zone1
    elements["zone2"] = zone2
    if "[" in line:
        meta_data: list = parts[2][1:-1].split(" ")
        for item in meta_data:
            parts: list = item.split("=")
            name: str = parts[0]
            data: int = int(parts[1])
            elements[name] = data
    return elements


def parser(filename: str) -> list[Zone | Connection]:
    graph: Graph = Graph()
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
                    zone_elements["name"],
                    zone_elements["xaxis"],
                    zone_elements["yaxis"],
                    zone_type=zone_elements.get("zone_type", "normal"),
                    color=zone_elements.get("color", "none"),
                    max_drones=zone_elements.get("max_drones", 1),
                )
                graph.create_graph(zone)
            if "connection" in line.split(" ")[0]:
                connection_elements: Dict = connection_instatiator(line)
                name_zone1: str = connection_elements["zone1"]
                name_zone2: str = connection_elements["zone2"]
                connection = Connection(
                    connection_elements["id"],
                    graph.zones[name_zone1],
                    graph.zones[name_zone2],
                    connection_elements.get("max_link_capacity", 1),
                )
                graph.create_graph(connection)
    return graph


if __name__ == "__main__":
    graph = parser("./maps/hard/02_capacity_hell.txt")
    print(graph.connections)
