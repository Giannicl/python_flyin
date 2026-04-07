from typing import Dict, Optional


class Zone:
    def __init__(
        self,
        name: str,
        xaxis: int,
        yaxis: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int = 1,
    ) -> None:
        self.name: str = name
        self.current_drone: Optional[str] = None
        self.xaxis: int = xaxis
        self.yaxis: int = yaxis
        self.zone_type: str = zone_type
        self.color: str = color
        self.max_drones: int = max_drones

    def __str__(self) -> str:
        return f"Zone_name: {self.name}, type: {self.zone_type}, coords: ({self.xaxis}, {self.yaxis})"

    def __repr__(self) -> str:
        return f"Zone_name: {self.name}, type: {self.zone_type}, coords: ({self.xaxis}, {self.yaxis})"


class Connection:
    def __init__(self, id: int, zone1: Zone, zone2: Zone, max_links: int = 1) -> None:
        self.id_digit: str = str(id)
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_links

    def __str__(self) -> str:
        return f"Zone 1: {self.zone1} and Zone 2: {self.zone2}"

    def __rep__(self) -> str:
        return f"Zone 1: {self.zone1} and Zone 2: {self.zone2}"


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, Connection] = {}
        self.nb_drones: int = 0

    def create_graph(self, element: Zone | Connection) -> None:
        if isinstance(element, Zone):
            self.zones[element.name] = element
        elif isinstance(element, Connection):
            self.connections[element.id_digit] = element

    def find_zone(self, zone_name: str) -> Zone | None:
        return self.zones.get(zone_name)

    def find_connection(self, connection_name: str) -> Connection | None:
        return self.connections.get(connection_name)
