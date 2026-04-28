from models import Zone, Connection, Graph
from typing import Dict, List


def validate_zone_type(zone_type: str) -> None:
    valid_zone_types: set[str] = {
        "start",
        "end",
        "normal",
        "restricted",
        "priority",
        "blocked",
    }
    if zone_type not in valid_zone_types:
        raise ValueError(f"[validate_zone_type] Invalid zone type: {zone_type}.")


def validate_capacity(value: int, key: str) -> None:
    if value <= 0:
        raise ValueError(
            f"[validate_capacity] {key} must be a positive integer, got {value}."
        )


def validate_unique_input(
    graph_elements: Dict,
    name_or_id: str,
) -> None:
    name_zone1: str
    name_zone2: str
    id_reversed: str
    if name_or_id in graph_elements:
        raise ValueError(f"[validate_unique_input] Duplicate element: {name_or_id}.")
    if "-" in name_or_id:
        name_zone1, name_zone2 = name_or_id.split("-")
        id_reversed = "-".join([name_zone2, name_zone1])
        if id_reversed in graph_elements:
            raise ValueError(
                f"[validate_unique_input] Duplicate element reversed connection: {id_reversed}"
            )


def validate_connection_zones_exist(
    graph: Graph, name_zone1: str, name_zone2: str
) -> None:
    if name_zone1 not in graph.zones:
        raise ValueError(f"[validate_connection_zones_exist] {name_zone1} does not exist.")
    if name_zone2 not in graph.zones:
        raise ValueError(f"[validate_connection_zones_exist] {name_zone2} does not exist.")


def validate_required_zones(graph: Graph) -> None:
    start_count: int = 0
    end_count: int = 0

    for zone in graph.zones.values():
        if zone.zone_type == "start":
            start_count += 1
        elif zone.zone_type == "end":
            end_count += 1

    if start_count != 1:
        raise ValueError(
            f"[validate_required_hubs] Expected 1 start zone, got {start_count}."
        )
    if end_count != 1:
        raise ValueError(
            f"[validate_required_hubs] Expected 1 end zone, got {end_count}."
        )


def validate_nb_drones(nb_drones: int) -> None:
    if nb_drones <= 0:
        raise ValueError(
            f"[validate_nb_drones] nb_drones must be present as a positive integer, got {nb_drones}"
        )


def initialise_obj(elements: Dict, key: str, value: int | str) -> None:
    elements[key] = value


def initialise_metadata(elements: Dict, meta_data: List[str]) -> None:
    for item in meta_data:
        parts: List[str] = item.split("=")
        key: str = parts[0]
        if key == "zone":
            key = "zone_type"
        value: int | str = int(parts[1]) if parts[1].isdigit() else parts[1]
        initialise_obj(elements, key, value)


def initialise_zone_cost(elements: Dict) -> None:
    zone_type: str = elements.get("zone_type", "normal")
    if zone_type == "restricted":
        elements["zone_cost"] = 2
    elif zone_type == "blocked":
        elements["zone_cost"] = 0
    else:
        elements["zone_cost"] = 1

def _parse_int(value: str, field: str) -> int:
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"[zone_instantiator] Invalid {field}: {value}")

def zone_instantiator(line: str) -> Dict:
    elements: Dict = {}
    parts: List[str] = line.split(" ", 4)
    size_parts: int = len(parts)

    if parts[0] == "start_hub:":
        initialise_obj(elements, "zone_type", "start")
    elif parts[0] == "end_hub:":
        initialise_obj(elements, "zone_type", "end")

    if size_parts > 1:
        initialise_obj(elements, "name", parts[1])
    if size_parts > 2:
        initialise_obj(elements, "xaxis", _parse_int(parts[2], "xaxis"))
    if size_parts > 3:
        initialise_obj(elements, "yaxis", _parse_int(parts[3], "yaxis"))

    if size_parts > 4 and "[" in line and "=" in line:
        meta_data: List[str] = parts[4][1:-1].split(" ")
        initialise_metadata(elements, meta_data)

    initialise_zone_cost(elements)
    return elements


def connection_instatiator(line: str) -> Dict:
    elements: Dict = {}
    parts: List[str] = line.split(" ", 2)
    size_parts: int = len(parts)

    zone1: str
    zone2: str
    zone1, zone2 = parts[1].split("-")

    initialise_obj(elements, "id", parts[1])
    initialise_obj(elements, "zone1", zone1)
    initialise_obj(elements, "zone2", zone2)

    if size_parts > 2 and "[" in line and "=" in line:
        meta_data: List[str] = parts[2][1:-1].split(" ")
        initialise_metadata(elements, meta_data)

    return elements


def create_zone(zone_elements: Dict) -> Zone:
    validate_capacity(zone_elements.get("max_drones", 1), "max_drones")
    if "xaxis" not in zone_elements or "yaxis" not in zone_elements:
        raise ValueError(f"Invalid zone definition: {zone_elements}")
    return Zone(
        zone_elements["name"],
        zone_elements["xaxis"],
        zone_elements["yaxis"],
        zone_type=zone_elements.get("zone_type", "normal"),
        color=zone_elements.get("color", "none"),
        max_drones=zone_elements.get("max_drones", 1),
        zone_cost=zone_elements.get("zone_cost", 0),
    )


def create_connection(connection_elements: Dict, graph: Graph) -> Connection:
    name_zone1: str = connection_elements["zone1"]
    name_zone2: str = connection_elements["zone2"]
    validate_connection_zones_exist(graph, name_zone1, name_zone2)
    validate_capacity(
        connection_elements.get("max_link_capacity", 1), "max_link_capacity"
    )
    return Connection(
        connection_elements["id"],
        graph.zones[name_zone1],
        graph.zones[name_zone2],
        connection_elements.get("max_link_capacity", 1),
    )


def parser(filename: str) -> Graph:
    graph: Graph = Graph()

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts: List[str] = line.split()

            if parts[0] == "nb_drones:":
                graph.nb_drones = int(parts[1])

            if "hub" in parts[0]:
                zone_elements: Dict = zone_instantiator(line)
                validate_unique_input(graph.zones, zone_elements["name"])
                zone: Zone = create_zone(zone_elements)
                validate_zone_type(zone.zone_type)
                graph.create_graph(zone)

            if parts[0] == "connection:":
                connection_elements: Dict = connection_instatiator(line)
                validate_unique_input(graph.connections, connection_elements["id"])
                connection: Connection = create_connection(connection_elements, graph)
                graph.create_graph(connection)

    validate_nb_drones(graph.nb_drones)
    validate_required_zones(graph)
    return graph


if __name__ == "__main__":
    graph = parser("./maps/hard/02_capacity_hell.txt")
