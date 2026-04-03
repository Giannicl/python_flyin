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


class Connection:
    def __init__(self, name: str, zone1: Zone, zone2: Zone, max_links: int = 1) -> None:
        self.name: str = name
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_links


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, Connection] = {}

    def create_graph(self, element: Zone | Connection) -> None:
        if isinstance(element, Zone):
            self.zones[element.name] = element
        elif isinstance(element, Connection):
            self.connections[element.name] = element

    def find_zone(self, zone_name: str) -> Zone | None:
        return self.zones.get(zone_name)

    def find_connection(self, connection_name: str) -> Connection | None:
        return self.connections.get(connection_name)
