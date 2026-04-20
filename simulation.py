from typing import Dict, List, Set
from file_parser import parser
from models import Zone, Graph, Drone, Connection
from algo import path_finder


class Simulation:
    def __init__(self, file_name: str) -> None:
        self.map: Graph = parser(file_name)
        self.drones: List[Drone] = [Drone(f"D{i+1}") for i in range(self.map.nb_drones)]
        self.zone_occupancy: Dict[str, List[Drone]] = {}
        self.connection_occupancy: Dict[str, List[Drone]] = {}
        self.turns: int = 0

    def _path_initialisor(self) -> None:
        start: Zone | None = None
        goal: Zone | None = None
        for zone in self.map.zones.values():
            if zone.zone_type == "start":
                start = zone
                print(start.name)
            if zone.zone_type == "end":
                goal = zone
                print(goal.name)
        if start is None or goal is None:
            raise ValueError("Map must contain both a start zone and an end zone.")
        path: List[Zone] | None = path_finder(self.map, start, goal)
        if path is None:
            raise ValueError("No path found from start to end")
        for drone in self.drones:
            drone.current_zone = start
            self.zone_occupancy.setdefault(start.name, []).append(drone)
            drone.path.extend(path[1:])

    def _is_zone_at_capacity(self, zone: Zone):
        if zone.zone_type == "end":
            return False
        return len(self.zone_occupancy.get(zone.name, [])) >= zone.max_drones

    def _is_connection_at_capacity(self, connection: Connection) -> bool:
        return (
            len(self.connection_occupancy.get(connection.id, []))
            >= self.connection.max_drones
        )

    def _remove_from_current_zone(self, drone: Drone) -> None:
        current_zone: Zone | None = drone.current_zone
        if current_zone is None:
            return
        if current_zone.name in self.zone_occupancy:
            self.zone_occupancy[current_zone.name].remove(drone)
            if not self.zone_occupancy[current_zone.name]:
                del self.zone_occupancy[current_zone.name]

    def _move_drone_to_zone(self, drone: Drone, next_zone: Zone) -> None:
        drone.move(next_zone)
        self.zone_occupancy.setdefault(next_zone.name, []).append(drone)
        drone.path.popleft()

    def _move_drone_throug_connection(self, drone: Drone, connection: Zone) -> None:
        self.connection_occupancy.setdefault(connection.id_name, []).append(drone)
        drone.current_connection = connection
        drone.in_transit = True
        drone.remaining_transit_turns: int = 1

    def _find_drone_goal(self, drone: Drone) -> Zone:
        for zone in self.map.zones.values():
            if zone.zone_type == "end":
                return zone
        raise ValueError("Map must contain an end zone.")

    def _full_zones(self) -> Set[str]:
        full_zones: Set[str] = set()
        for zone_name, drones in self.zone_occupancy.items():
            zone: Zone = self.map.zones[zone_name]
            if len(drones) >= zone.max_drones:
                full_zones.add(zone_name)
        return full_zones

    def _new_path_calculator(self, drone: Drone) -> List[Zone] | None:
        current_zone: Zone = drone.current_zone
        if current_zone is None:
            return
        goal: Zone = self._find_drone_goal(drone)
        full_zones: Set[str] = self._full_zones()
        full_zones.discard(current_zone.name)
        new_path = path_finder(self.map, current_zone, goal, full_zones=full_zones)
        if new_path is None or len(new_path) <= 1:
            return None
        return new_path[1:]

    def _path_cost(self, path: List[Zone]) -> int:
        cost_zone_type: Dict = {
            "start": 0,
            "end": 0,
            "normal": 0,
            "priority": 1,
            "restricted": 2,
        }
        cost: int = 0
        for zone in path:
            cost += cost_zone_type.get(zone.zone_type, 0)
        return cost

    def _should_reroute_path(self, drone: Drone, new_path: List[Zone] | None) -> bool:
        if new_path is None:
            return False
        wait_cost: int = self._path_cost(list(drone.path)) + 1
        reroute_cost: int = self._path_cost(new_path)
        return reroute_cost < wait_cost

    def _reroute_drone(self, drone: Drone, new_path: List[Zone]) -> None:
        drone.path.clear()
        drone.path.extend(new_path)

    def _handle_blocked_drone(self, drone: Drone) -> None:
        new_path: List[Zone] = self._new_path_calculator(drone)
        if self._should_reroute_path(drone, new_path):
            self._reroute_drone(drone, new_path)

    def move_drones(self) -> None:
        for drone in self.drones:
            if not drone.path:
                continue
            current_zone: Zone | None = drone.current_zone
            if current_zone is None:
                raise ValueError(f"{drone.drone_id} has no current zone. [move_drones]")
            next_zone: Zone = drone.path[0]
            if self._is_zone_at_capacity(next_zone):
                self._handle_blocked_drone(drone)
                continue
            self._remove_from_current_zone(drone)
            self._move_drone_to_zone(drone, next_zone)

    def output(self) -> None:
        for drone in self.drones:
            if drone.current_zone is not None:
                print(f"{drone.drone_id} - {drone.current_zone.name} ", end="")
        print()

    def run(self) -> None:
        self._path_initialisor()
        self.output()
        while any(drone.path for drone in self.drones):
            self.turns += 1
            self.move_drones()
            self.output()


if __name__ == "__main__":
    sim = Simulation("./maps/hard/01_maze_nightmare.txt")
    sim.run()
