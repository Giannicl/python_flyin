from models import Zone, Connection, Graph
from typing import Dict, List


def zone_instantiator(line: str) -> Dict:
    elements: Dict = {}
    parts: List = line.split(" ", 4)
    elements["name"] = parts[1]
    elements["xaxis"] = int(parts[2])
    elements["yaxis"] = int(parts[3])
    if "start" in parts[0]:
        elements["zone_type"] = "start"
    elif "end" in parts[0]:
        elements["zone_type"] = "end"
    if "[" in line:
        meta_data: List = parts[4][1:-1].split(" ")
        for item in meta_data:
            parts: list = item.split("=")
            name: str = parts[0]
            if name == "zone" and "zone_type" not in elements:
                name: str = "zone_type"
            data: int | str = int(parts[1]) if parts[1].isdigit() else parts[1]
            elements[name] = data
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
