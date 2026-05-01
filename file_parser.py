from models import Zone, Connection, Graph
from typing import Dict, List, Any


def validate_zone_type(zone_type: str) -> None:
    """Validates that a zone type is one of the accepted values.

    Args:
        zone_type: The zone type string to validate.

    Raises:
        ValueError: If the zone type is not one of 'start', 'end', 'normal',
        'restricted', 'priority', or 'blocked'.
    """
    valid_zone_types: set[str] = {
        "start",
        "end",
        "normal",
        "restricted",
        "priority",
        "blocked",
    }
    if zone_type not in valid_zone_types:
        raise ValueError("[validate_zone_type] "
                         f"Invalid zone type: {zone_type}.")


def validate_capacity(value: int, key: str) -> None:
    """Validates that a capacity value is a positive integer.

    Args:
        value: The capacity value to validate.
        key: The name of the field being validated, used in the error message.

    Raises:
        ValueError: If the value is not a positive integer.
    """
    if value <= 0:
        raise ValueError(
            f"[validate_capacity] {key} "
            f"must be a positive integer, got {value}."
        )


def validate_unique_input(
    graph_elements: Dict[str, Any],
    name_or_id: str,
) -> None:
    """Validates that a zone name or
    connection ID has not already been defined.

    Also checks for duplicate connections
    in reverse order (e.g., 'a-b' and 'b-a').

    Args:
        graph_elements: Dictionary of already registered zones or connections.
        name_or_id: The zone name or connection ID to check.

    Raises:
        ValueError: If the name or ID is already present in graph_elements,
            or if its reverse connection already exists.
    """
    name_zone1: str
    name_zone2: str
    id_reversed: str
    if name_or_id in graph_elements:
        raise ValueError("[validate_unique_input] "
                         f"Duplicate element: {name_or_id}.")
    if "-" in name_or_id:
        name_zone1, name_zone2 = name_or_id.split("-")
        id_reversed = "-".join([name_zone2, name_zone1])
        if id_reversed in graph_elements:
            raise ValueError(
                "[validate_unique_input] Duplicate element "
                f"reversed connection: {id_reversed}"
            )


def validate_connection_zones_exist(
    graph: Graph, name_zone1: str, name_zone2: str
) -> None:
    """Validates that both zones referenced by a connection exist in the graph.

    Args:
        graph: The navigation graph to check against.
        name_zone1: The name of the first zone.
        name_zone2: The name of the second zone.

    Raises:
        ValueError: If either zone does not exist in the graph.
    """
    if name_zone1 not in graph.zones:
        raise ValueError(
            f"[validate_connection_zones_exist] {name_zone1} does not exist."
        )
    if name_zone2 not in graph.zones:
        raise ValueError(
            f"[validate_connection_zones_exist] {name_zone2} does not exist."
        )


def validate_required_zones(graph: Graph) -> None:
    """Validates that the graph contains exactly one start and one end zone.

    Args:
        graph: The navigation graph to validate.

    Raises:
        ValueError: If the graph does not contain exactly one start zone
            and one end zone.
    """
    start_count: int = 0
    end_count: int = 0

    for zone in graph.zones.values():
        if zone.zone_type == "start":
            start_count += 1
        elif zone.zone_type == "end":
            end_count += 1

    if start_count != 1:
        raise ValueError(
            "[validate_required_hubs] Expected 1 start zone, "
            f"got {start_count}."
        )
    if end_count != 1:
        raise ValueError(
            f"[validate_required_hubs] Expected 1 end zone, got {end_count}."
        )


def validate_nb_drones(nb_drones: int | Any) -> int:
    """Validates and returns the number of drones as a positive integer.

    Args:
        nb_drones: The value to validate, can be any type.

    Returns:
        The validated number of drones as an integer.

    Raises:
        ValueError: If the value is not numeric or not a positive integer.
    """
    try:
        value = int(nb_drones)
    except ValueError:
        raise ValueError("[validate_nb_drones] must be numeric")
    if value <= 0:
        raise ValueError(
            "[validate_nb_drones] nb_drones must be present "
            f"as a positive integer, got {nb_drones}"
        )
    return value


def validate_connection_format(connection_id: str) -> tuple[str, str]:
    """Validates and parses a connection ID into its two zone names.

    Args:
        connection_id: The connection string in 'zone1-zone2' format.

    Returns:
        A tuple of (zone1_name, zone2_name).

    Raises:
        ValueError: If the connection ID is not in the correct format,
            does not contain exactly two zones, or either zone name is empty.
    """
    if "-" not in connection_id:
        raise ValueError(
            "[parse_connection_zones] Connection must use zone1-zone2 format."
        )
    connection_parts: list[str] = connection_id.split("-")
    if len(connection_parts) != 2:
        raise ValueError(
            "[parse_connection_zones] "
            "Connection must contain exactly two zones."
        )
    zone1, zone2 = connection_parts
    if not zone1 or not zone2:
        raise ValueError("[parse_connection_zones] "
                         "Connection zones cannot be empty.")
    return zone1, zone2


def initialise_obj(elements: Dict[str, int | str],
                   key: str, value: int | str) -> None:
    """Stores a key-value pair in the elements Dictionary.

    Args:
        elements: The Dictionary to update.
        key: The key to store the value under.
        value: The value to store.
    """
    elements[key] = value


def initialise_metadata(elements: Dict[str, int | str],
                        meta_data: List[str]) -> None:
    """Parses and stores metadata key-value pairs into the elements Dictionary.

    Args:
        elements: The Dictionary to update with parsed metadata.
        meta_data: A list of strings in 'key=value' format representing
            the metadata fields to parse.
    """
    for item in meta_data:
        parts: List[str] = item.split("=")
        key: str = parts[0]
        if key == "zone":
            key = "zone_type"
        value: int | str = int(parts[1]) if parts[1].isdigit() else parts[1]
        initialise_obj(elements, key, value)


def initialise_zone_cost(elements: Dict[str, Any]) -> None:
    """Sets the movement cost of a zone based on its type.

    Restricted zones cost 2 turns, blocked zones cost 0, and all
    other zone types cost 1 turn.

    Args:
        elements: The Dictionary containing the zone's attributes,
            including its zone_type. Updated in place with the zone_cost.
    """
    zone_type: str = elements.get("zone_type", "normal")
    if zone_type == "restricted":
        elements["zone_cost"] = 2
    elif zone_type == "blocked":
        elements["zone_cost"] = 0
    else:
        elements["zone_cost"] = 1


def _parse_int(value: str, field: str) -> int:
    """Parses a string into an integer.

    Args:
        value: The string to parse.
        field: The name of the field being parsed, used in the error message.

    Returns:
        The parsed integer value.

    Raises:
        ValueError: If the string cannot be converted to an integer.
    """
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"[zone_instantiator] Invalid {field}: {value}")


def zone_instantiator(line: str) -> Dict[str, int | str]:
    """Parses a zone definition line into a Dictionary of zone attributes.

    Args:
        line: A raw line from the map file defining a zone.

    Returns:
        A Dictionary containing the zone's attributes including name,
        xaxis, yaxis, zone_type, and zone_cost, plus any optional
        metadata fields.
    """
    elements: Dict[str, int | str] = {}
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


def connection_instatiator(line: str) -> Dict[str, str | Zone]:
    """Parses a connection definition line
    into a Dictionary of connection attributes.

    Args:
        line: A raw line from the map file defining a connection.

    Returns:
        A Dictionary containing the connection's attributes including
        id, zone1, zone2, and any optional metadata fields.

    Raises:
        ValueError: If the connection format is invalid.
    """
    elements: Dict[str, Any] = {}
    parts: List[str] = line.split(" ", 2)
    if len(parts) < 2:
        raise ValueError("[connection_instatiator] Invalid connection format.")

    zone1, zone2 = validate_connection_format(parts[1])
    initialise_obj(elements, "id", parts[1])
    initialise_obj(elements, "zone1", zone1)
    initialise_obj(elements, "zone2", zone2)
    if len(parts) > 2 and "[" in line and "=" in line:
        meta_data: List[str] = parts[2][1:-1].split(" ")
        initialise_metadata(elements, meta_data)
    return elements


def create_zone(zone_elements: Dict[str, Any]) -> Zone:
    """Creates and returns a Zone instance from a Dictionary of attributes.

    Args:
        zone_elements: A Dictionary containing the zone's attributes
            as parsed from the map file.

    Returns:
        A Zone instance initialised with the provided attributes.

    Raises:
        ValueError: If the capacity is invalid or coordinates are missing.
    """
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


def create_connection(connection_elements: Dict[str, Any],
                      graph: Graph) -> Connection:
    """Creates and returns a Connection
    instance from a Dictionary of attributes.

    Args:
        connection_elements: A Dictionary containing
        the connection's attributes
        as parsed from the map file.
        graph: The navigation graph used to look up the referenced zones.

    Returns:
        A Connection instance linking the two specified zones.

    Raises:
        ValueError: If either zone does not exist or the capacity is invalid.
    """
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
    """Parses a map file and builds a Graph instance from its contents.

    Args:
        filename: Path to the map file to parse.

    Returns:
        A fully constructed Graph instance containing all zones,
        connections, and drone count defined in the file.

    Raises:
        ValueError: If the file is missing required fields, contains
            invalid values, duplicate definitions, or malformed syntax.
        FileNotFoundError: If the specified file does not exist.
    """
    graph: Graph = Graph()

    with open(filename, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts: List[str] = line.split()

            if parts[0] == "nb_drones:":
                if len(parts) != 2:
                    raise ValueError("[parser] Invalid nb_drones format.")
                graph.nb_drones = validate_nb_drones(parts[1])

            if "hub" in parts[0]:
                zone_elements: Dict[str, Any] = zone_instantiator(line)
                validate_unique_input(graph.zones, zone_elements["name"])
                zone: Zone = create_zone(zone_elements)
                validate_zone_type(zone.zone_type)
                graph.create_graph(zone)

            if parts[0] == "connection:":
                connection_elements: Dict[str,
                                          Any] = connection_instatiator(line)
                validate_unique_input(graph.connections,
                                      connection_elements["id"])
                connection: Connection = create_connection(
                    connection_elements, graph)
                graph.create_graph(connection)
    if graph.nb_drones == 0:
        raise ValueError("[parser] Missing or invalid nb_drones.")
    validate_required_zones(graph)
    return graph


if __name__ == "__main__":
    graph = parser("./maps/hard/02_capacity_hell.txt")
