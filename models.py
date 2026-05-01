from __future__ import annotations
from typing import Dict, Optional, List
from collections import deque


class Zone:
    """Represents a node in the drone navigation graph.

    Attributes:
        name: Unique identifier for the zone.
        xaxis: X coordinate on the map.
        yaxis: Y coordinate on the map.
        zone_type: Type of zone. One of 'start', 'end', 'normal',
            'restricted', 'priority', or 'blocked'.
        color: Display color for visualization.
        max_drones: Maximum number of drones allowed simultaneously.
        zone_cost: Movement cost in turns to enter this zone.
        current_drone: ID of the drone currently occupying the zone, or None.
    """

    def __init__(
        self,
        name: str,
        xaxis: int,
        yaxis: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int = 1,
        zone_cost: int = 0,
    ) -> None:
        self.name: str = name
        self.current_drone: Optional[str] = None
        self.xaxis: int = xaxis
        self.yaxis: int = yaxis
        self.zone_type: str = zone_type
        self.color: str = color
        self.max_drones: int = max_drones
        self.zone_cost: int = zone_cost

    def __str__(self) -> str:
        """Returns a human-readable string
        representation of the zone."""
        return (f"Zone_name: {self.name}, "
                f"type: {self.zone_type}, "
                f"coords: ({self.xaxis}, {self.yaxis})")

    def __repr__(self) -> str:
        """Returns a human-readable string
        representation of the zone."""
        return (f"Zone_name: {self.name}, "
                f"type: {self.zone_type}, "
                f"coords: ({self.xaxis}, {self.yaxis})")

    def __lt__(self, other: "Zone") -> bool:
        """Compares zones by name for heap ordering support.

        Args:
            other: The zone to compare against.

        Returns:
            True if this zone's name is alphabetically less than the other's.
        """
        return self.name < other.name


class Connection:
    """Represents a bidirectional edge
    between two zones in the navigation graph.

    Attributes:
        id: Unique identifier for the connection in 'zone1-zone2' format.
        zone1: The first zone of the connection.
        zone2: The second zone of the connection.
        max_link_capacity: Maximum number of drones that can traverse
            this connection simultaneously.
    """

    def __init__(
        self, id: str, zone1: Zone, zone2: Zone, max_link_capacity: int = 1
    ) -> None:
        self.id: str = id
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_link_capacity

    def __str__(self) -> str:
        """Returns a human-readable string representation of the connection."""
        return (f"Zone 1: {self.zone1}, Zone 2: {self.zone2}, "
                f"max_link_capacity: {self.max_link_capacity}")

    def __repr__(self) -> str:
        """Returns a human-readable string representation of the connection."""
        return (f"Zone 1: {self.zone1}, Zone 2: {self.zone2}, "
                f"max_link_capacity: {self.max_link_capacity}")


class Graph:
    """Represents the drone navigation graph as an adjacency structure.

    Attributes:
        zones: Dictionary mapping zone names to Zone instances.
        connections: Dictionary mapping connection IDs to Connection instances.
        nb_drones: Total number of drones to simulate.
        neighbours: Dictionary mapping zone names to lists of adjacent zones.
    """

    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, Connection] = {}
        self.nb_drones: int = 0
        self.neighbours: Dict[str, List[Zone]] = {}

    def create_graph(self, element: Zone | Connection) -> None:
        """Adds a zone or connection to the graph.

        Args:
            element: A Zone or Connection instance to add. If a Zone, it is
                stored in the zones Dictionary. If a Connection, it is stored
                in the connections Dictionary and both zones are updated in
                the neighbours map.
        """
        if isinstance(element, Zone):
            self.zones[element.name] = element
        elif isinstance(element, Connection):
            self.connections[element.id] = element
            self.neighbours.setdefault(element.zone1.name,
                                       []).append(element.zone2)
            self.neighbours.setdefault(element.zone2.name,
                                       []).append(element.zone1)

    def find_zone(self, zone_name: str) -> Zone | None:
        """Returns the zone with the given name, or None if not found.

        Args:
            zone_name: The name of the zone to look up.

        Returns:
            The Zone instance if found, otherwise None.
        """
        return self.zones.get(zone_name)

    def find_connection_id(self, connection_id: str) -> Connection | None:
        """Returns the connection with the given ID, or None if not found.

        Args:
            connection_id: The connection ID in 'zone1-zone2' format.

        Returns:
            The Connection instance if found, otherwise None.
        """
        return self.connections.get(connection_id)

    def find_connection_zones(self, zone1: Zone,
                              zone2: Zone) -> Connection | None:
        """Returns the connection between two zones, or None if not found.

        Checks both directions of the connection (zone1-zone2 and zone2-zone1).

        Args:
            zone1: The first zone of the connection.
            zone2: The second zone of the connection.

        Returns:
            The Connection instance if found, otherwise None.
        """
        connection_id: str = f"{zone1.name}-{zone2.name}"
        reverse_connection_id: str = f"{zone2.name}-{zone1.name}"
        if connection_id in self.connections:
            return self.connections[connection_id]
        if reverse_connection_id in self.connections:
            return self.connections[reverse_connection_id]
        return None

    def find_neighbours(self, zone_name: str) -> List[Zone]:
        """Returns the list of zones adjacent to the given zone.

        Args:
            zone_name: The name of the zone to look up.

        Returns:
            A list of Zone instances connected to the given zone,
            or an empty list if the zone has no neighbours.
        """
        return self.neighbours.get(zone_name, [])


class Drone:
    """Represents a drone navigating through the graph.

    Attributes:
        drone_id: Unique identifier for the drone (e.g., 'D1', 'D2').
        current_zone: The zone the drone is currently occupying, or None.
        path: Ordered queue of zones the drone still needs to traverse.
        turns: Total number of turns the drone has taken.
        in_transit: Whether the drone is currently mid-transit on a connection.
        current_connection: The connection the drone is traversing, or None.
        remaining_transit_turns:
        Number of turns left to complete current transit.
    """

    def __init__(self, drone_id: str) -> None:
        self.drone_id: str = drone_id
        self.current_zone: Zone | None = None
        self.path: deque[Zone] = deque([])
        self.turns: int = 0
        self.in_transit: bool = False
        self.current_connection: Connection | None = None
        self.remaining_transit_turns: int = 0

    def move(self, next_zone: Zone) -> None:
        """Moves the drone to the next zone and increments its turn counter.

        Args:
        next_zone: The zone to move the drone to.
        """
        self.turns += 1
        self.current_zone = next_zone

    def add_path(self, path: List[Zone]) -> None:
        """Sets the drone's path and initial position.

        Args:
        path: An ordered list of zones from start to goal.
        """
        for item in path:
            self.path.append(item)
        self.current_zone = path[0]

    def __str__(self) -> str:
        """Returns the drone's unique identifier."""
        return f"{self.drone_id}"

    def __repr__(self) -> str:
        """Returns the drone's unique identifier."""
        return f"{self.drone_id}"
