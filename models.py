from __future__ import annotations
from typing import Dict, Optional, List
from collections import deque


class Zone:
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
        return f"Zone_name: {self.name}, type: {self.zone_type}, coords: ({self.xaxis}, {self.yaxis})"

    def __repr__(self) -> str:
        return f"Zone_name: {self.name}, type: {self.zone_type}, coords: ({self.xaxis}, {self.yaxis})"

    def __lt__(self, other: "Zone") -> bool:
        return self.name < other.name


class Connection:
    def __init__(self, id: str, zone1: Zone, zone2: Zone, max_drones: int = 1) -> None:
        self.id_name: str = id
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_drones: int = max_drones

    def __str__(self) -> str:
        return (
            f"Zone 1: {self.zone1}, Zone 2: {self.zone2}, max_drones: {self.max_drones}"
        )

    def __repr__(self) -> str:
        return (
            f"Zone 1: {self.zone1}, Zone 2: {self.zone2}, max_drones: {self.max_drones}"
        )


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, Connection] = {}
        self.nb_drones: int = 0
        self.neighbours: Dict[str, List[Zone]] = {}

    def create_graph(self, element: Zone | Connection) -> None:
        if isinstance(element, Zone):
            self.zones[element.name] = element
        elif isinstance(element, Connection):
            self.connections[element.id_name] = element
            self.neighbours.setdefault(element.zone1.name, []).append(element.zone2)
            self.neighbours.setdefault(element.zone2.name, []).append(element.zone1)

    def find_zone(self, zone_name: str) -> Zone | None:
        return self.zones.get(zone_name)

    def find_connection_id(self, connection_id: str) -> Connection | None:
        return self.connections.get(connection_id)

    def find_connection_zones(self, zone1: Zone, zone2: Zone) -> Connection | None:
        connection_id: str = f"{zone1.name}-{zone2.name}"
        reverse_connection_id: str = f"{zone2.name}-{zone1.name}"
        if connection_id in self.connections:
            return self.connections[connection_id]
        if reverse_connection_id in self.connections:
            return self.connections[reverse_connection_id]
        return None

    def find_neighbours(self, zone_name: str) -> List[Zone]:
        return self.neighbours.get(zone_name, [])


class Drone:
    def __init__(self, drone_id: str) -> None:
        self.drone_id: str = drone_id
        self.current_zone: Zone | None = None
        self.path: deque[Zone] = deque([])
        self.turns: int = 0
        self.in_transit: bool = False
        self.current_connection: Connection | None = None
        self.remaining_transit_turns: int = 0

    def move(self, next_zone: Zone) -> None:
        self.turns += 1
        self.current_zone = next_zone

    def add_path(self, path: List[Zone]) -> None:
        for item in path:
            self.path.append(item)
        self.current_zone = path[0]

    def __str__(self) -> None:
        return f"{self.drone_id}"

    def __repr__(self) -> None:
        return f"{self.drone_id}"
