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
        self.turn_output: List[str] = []
        self.zone_arrival_reservations: Dict[int, Dict[str, int]] = {}
        self.frames: List[Dict[str, str]] = []

    def _record_frame(self) -> None:
        frame: Dict[str, str] = {}
        for zone_name, drones in self.zone_occupancy.items():
            for drone in drones:
                frame[drone.drone_id] = zone_name
        for connection_id, drones in self.connection_occupancy.items():
            for drone in drones:
                frame[drone.drone_id] = connection_id
        self.frames.append(frame)

    def _path_initialisor(self) -> None:
        start: Zone | None = None
        goal: Zone | None = None
        for zone in self.map.zones.values():
            if zone.zone_type == "start":
                start = zone
            if zone.zone_type == "end":
                goal = zone
        if start is None or goal is None:
            raise ValueError(
                "[_path_initialisor] Map must contain both a start zone and an end zone."
            )
        path: List[Zone] | None = path_finder(self.map, start, goal)
        if path is None:
            raise ValueError("[_path_initialisor] No path found from start to end")
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
            >= connection.max_link_capacity
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
        self.turn_output.append(f"{drone.drone_id}-{next_zone.name}")
        drone.path.popleft()

    def _move_drone_through_connection(
        self, drone: Drone, connection: Connection, next_zone: Zone
    ) -> None:
        self.connection_occupancy.setdefault(connection.id, []).append(drone)
        self.turn_output.append(f"{drone.drone_id}-{connection.id}")
        drone.current_connection = connection
        drone.in_transit = True
        drone.remaining_transit_turns = next_zone.zone_cost - 1

    def _find_drone_goal(self, drone: Drone) -> Zone:
        for zone in self.map.zones.values():
            if zone.zone_type == "end":
                return zone
        raise ValueError("[_find_drone_goal] Map must contain an end zone.")

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
        cost: int = 0
        for zone in path:
            cost += zone.zone_cost
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

    def _get_transit_connection(self, drone: Drone) -> Connection:
        connection: Connection | None = drone.current_connection
        if connection is None:
            raise ValueError(
                f"[_get_transit_connection] missing connection for {drone.drone_id}"
            )
        return connection

    def _get_transit_destination(self, drone: Drone, connection: Connection) -> Zone:
        return (
            connection.zone2
            if drone.current_zone == connection.zone1
            else connection.zone1
        )
   
    def _release_connection(self, drone: Drone, connection: Connection) -> None:
        self.connection_occupancy[connection.id].remove(drone)
        if not self.connection_occupancy[connection.id]:
            del self.connection_occupancy[connection.id]

    def _release_arrival_reservation(self, zone: Zone, arrival_turn: int) -> None:
        if arrival_turn not in self.zone_arrival_reservations:
            return
        if zone.name not in self.zone_arrival_reservations[arrival_turn]:
            return
        self.zone_arrival_reservations[arrival_turn][zone.name] -= 1
        if self.zone_arrival_reservations[arrival_turn][zone.name] == 0:
            del self.zone_arrival_reservations[arrival_turn][zone.name]
        if not self.zone_arrival_reservations[arrival_turn]:
            del self.zone_arrival_reservations[arrival_turn]

    def _clear_transit_state(self, drone: Drone) -> None:
        drone.in_transit = False
        drone.current_connection = None
        drone.remaining_transit_turns = 0

    def _process_transit_drone(self, drone: Drone) -> None:
        connection: Connection = self._get_transit_connection(drone) 
        drone.remaining_transit_turns -= 1 
        if drone.remaining_transit_turns > 0:
            self.turn_output.append(f"{drone.drone_id}-{connection.id}")
            return
        next_zone: Zone = self._get_transit_destination(drone, connection)
        self._release_connection(drone, connection)
        arrival_turn: int = self.turns
        self._release_arrival_reservation(next_zone, arrival_turn)
        self._clear_transit_state(drone)    


        self._move_drone_to_zone(drone, next_zone)

    def _process_move_drone(
        self, drone: Drone, connection: Connection, next_zone: Zone
    ) -> None:
        if next_zone.zone_cost > 1:
            arrival_turn: int = self._arrival_turn(next_zone)
            if (
                not self._has_arrival_capacity(next_zone, arrival_turn)
                or self._is_connection_at_capacity(connection)):
                self._handle_blocked_drone(drone)
                return
            self._reserve_arrival(next_zone, arrival_turn)
            self._remove_from_current_zone(drone)
            self._move_drone_through_connection(drone, connection, next_zone)
        else:
            if self._is_zone_at_capacity(next_zone):
                self._handle_blocked_drone(drone)
                return
            self._remove_from_current_zone(drone)
            self._move_drone_to_zone(drone, next_zone)


    def _arrival_turn(self, next_zone: Zone) -> int:
        return self.turns + next_zone.zone_cost - 1

    def _reserved_arrivals(self, zone: Zone, arrival_turn: int) -> int:
        return self.zone_arrival_reservations.get(arrival_turn, {}).get(zone.name, 0)

    def _reserve_arrival(self, zone: Zone, arrival_turn: int) -> None:
        self.zone_arrival_reservations.setdefault(arrival_turn, {})
        self.zone_arrival_reservations[arrival_turn][zone.name] = (
            self.zone_arrival_reservations[arrival_turn].get(zone.name, 0) + 1
        )

    def _has_arrival_capacity(self, zone: Zone, arrival_turn: int) -> bool:
        if zone.zone_type == "end":
            return True
        reserved_occupancy: int = self._reserved_arrivals(zone, arrival_turn)
        return reserved_occupancy < zone.max_drones


    def move_drones(self) -> None:
        for drone in self.drones:
            if not drone.path:
                continue
            if drone.in_transit:
                self._process_transit_drone(drone)
                continue
            current_zone: Zone | None = drone.current_zone
            if current_zone is None:
                raise ValueError(f"[move_drones] {drone.drone_id} has no current zone.")
            next_zone: Zone = drone.path[0]
            if not next_zone:
                raise ValueError(f"[move_drones] {drone.drone_id} has no next zone")
            connection: Connection | None = self.map.find_connection_zones(
                current_zone, next_zone
            )
            if connection is None:
                raise ValueError(
                    f"[move_drones] No connection found between {current_zone.name} and {next_zone.name}"
                )
            if next_zone.zone_type == "blocked":
                self._handle_blocked_drone(drone)
                continue
            self._process_move_drone(drone, connection, next_zone)

    def output(self) -> None:
        if self.turn_output:
            print(" ".join(sorted(self.turn_output)))

    def run(self) -> None:
        self._path_initialisor()
        self._record_frame()
        while any(drone.path for drone in self.drones):
            self.turns += 1
            self.turn_output = []
            self.move_drones()
            self._record_frame()
            self.output()


if __name__ == "__main__":
    sim = Simulation("./maps/hard/01_maze_nightmare.txt")
    sim.run()
