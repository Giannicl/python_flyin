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
    
    def __lt__(self, other: "Zone") -> bool:
        return self.name < other.name




class Connection:
    def __init__(self, id: str, zone1: Zone, zone2: Zone, max_links: int = 1) -> None:
        self.id_name: str = id
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_links

    def __str__(self) -> str:
        return f"Zone 1: {self.zone1}, Zone 2: {self.zone2}, max_link_capacity: {self.max_link_capacity}"

    def __repr__(self) -> str:
        return f"Zone 1: {self.zone1}, Zone 2: {self.zone2}, max_link_capacity: {self.max_link_capacity}"


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, Connection] = {}
        self.nb_drones: int = 0

    def create_graph(self, element: Zone | Connection) -> None:
        if isinstance(element, Zone):
            self.zones[element.name] = element
        elif isinstance(element, Connection):
            self.connections[element.id_name] = element

    def find_zone(self, zone_name: str) -> Zone | None:
        return self.zones.get(zone_name)

    def find_connection(self, connection_id: str) -> Connection | None:
        return self.connections.get(connection_id)

    def find_neighbours(self, zone_name: str) -> List[Zone]:
        neighbours: List = []
        for id_name in self.connections:
            parts = id_name.split("-")
            if zone_name == parts[0] or zone_name == parts[1]:
                neighbours.append(self.zones[parts[0]] if parts[0] != zone_name else self.zones[parts[1]])                                   
        return neighbours

class Drone:
    def __init__(self, drone_id: str) -> None:
        self.drone_id: str = drone_id
        self.current_zone: Zone = None
        self.path: deque = deque([])
        self.turns: int = 0

    def move(self, start: Zone, next_zone: Zone) -> None:
        self.current_zone = start
        print(f"'{self.drone_id}' has moved from {self.current_zone.name} to {next_zone.name}")
        self.turns += 1
        #print(f"{self.turns} turn")
        self.current_zone = next_zone

    def add_path(self, path: List[Zone]) -> None:
        for item in path: 
            self.path.append(item)
