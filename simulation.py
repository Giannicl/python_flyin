from typing import Dict, List, Set
from file_parser import parser
from models import Zone, Graph, Drone, Connection
from algo import path_finder


class Simulation:
    """Manages the turn-based drone routing simulation.

    Attributes:
        graph: The navigation graph containing all zones and connections.
        drones: List of all drones participating in the simulation.
        zone_occupancy: Dictionary mapping zone names to lists of drones
            currently occupying them.
        connection_occupancy: Dictionary mapping connection IDs to lists
            of drones currently traversing them.
        turn_connection_usage: Dictionary tracking how many drones have
            used each connection in the current turn.
        turns: Total number of simulation turns elapsed.
        turn_output: List of movement strings to print for the current turn.
        zone_arrival_reservations: Dictionary mapping future turn numbers to
            Dictionaries of zone names and their reserved arrival counts.
        frames: List of frame snapshots for graphical visualization.
        capacity_info_enabled: Whether to print capacity info each turn.
    """

    RGB_COLOR_MAP: Dict[str, tuple[int, int, int]] = {
        "red": (220, 50, 50),
        "green": (50, 180, 90),
        "blue": (50, 100, 220),
        "yellow": (220, 200, 50),
        "purple": (140, 70, 180),
        "orange": (230, 130, 40),
        "brown": (130, 80, 40),
        "gold": (220, 170, 40),
        "maroon": (120, 30, 50),
        "violet": (150, 80, 200),
        "crimson": (180, 30, 60),
        "darkred": (100, 20, 20),
        "black": (40, 40, 40),
        "gray": (130, 130, 130),
        "rainbow": (200, 80, 220),
        "none": (255, 255, 255),
    }
    ANSI_RESET = "\033[0m"

    def __init__(self, file_name: str) -> None:
        self.graph: Graph = parser(file_name)
        self.drones: List[Drone] = [
            Drone(f"D{i+1}") for i in range(self.graph.nb_drones)
        ]
        self.zone_occupancy: Dict[str, List[Drone]] = {}
        self.connection_occupancy: Dict[str, List[Drone]] = {}
        self.turn_connection_usage: Dict[str, int] = {}
        self.turns: int = 0
        self.turn_output: List[str] = []
        self.zone_arrival_reservations: Dict[int, Dict[str, int]] = {}
        self.frames: List[Dict[str, str]] = []
        self.capacity_info_enabled: bool = False

    def _print_capacity_info(self) -> None:
        """Prints the current drone occupancy for all zones and connections."""
        zone_info = []
        for zone_name, zone in self.graph.zones.items():
            current = len(self.zone_occupancy.get(zone_name, []))
            zone_info.append(f"{zone_name}: {current}/{zone.max_drones}")

        connection_info = []
        for conn_id, conn in self.graph.connections.items():
            current = len(self.connection_occupancy.get(conn_id, []))
            connection_info.append(f"{conn_id}: "
                                   f"{current}/{conn.max_link_capacity}")

        print(" | ".join(zone_info))
        print(" | ".join(connection_info))

    def _record_frame(self) -> None:
        """Records the current positions of all drones
        as a visualization frame."""
        frame: Dict[str, str] = {}
        for zone_name, drones in self.zone_occupancy.items():
            for drone in drones:
                frame[drone.drone_id] = zone_name
        for connection_id, drones in self.connection_occupancy.items():
            for drone in drones:
                frame[drone.drone_id] = connection_id
        self.frames.append(frame)

    def _path_initialisor(self) -> None:
        """Initialises drone paths and places all drones at the start zone.

        Finds the start and end zones, computes the initial shortest path,
        and assigns it to all drones.

        Raises:
            ValueError: If no start or end zone is found, or if no valid
                path exists between them.
        """
        start: Zone | None = None
        goal: Zone | None = None
        for zone in self.graph.zones.values():
            if zone.zone_type == "start":
                start = zone
            if zone.zone_type == "end":
                goal = zone
        if start is None or goal is None:
            raise ValueError(
                "[_path_initialisor] "
                "Map must contain both a start zone and an end zone."
            )
        path: List[Zone] | None = path_finder(self.graph, start, goal)
        if path is None:
            raise ValueError("[_path_initialisor] "
                             "No path found from start to end")
        for drone in self.drones:
            drone.current_zone = start
            self.zone_occupancy.setdefault(start.name, []).append(drone)
            drone.path.extend(path[1:])

    def _is_zone_at_capacity(self, zone: Zone) -> bool:
        """Checks whether a zone has reached its maximum drone capacity.

        The end zone is never considered at capacity.

        Args:
            zone: The zone to check.

        Returns:
        True if the zone is at or above its maximum capacity, otherwise False.
        """
        if zone.zone_type == "end":
            return False
        return len(self.zone_occupancy.get(zone.name, [])) >= zone.max_drones

    def _remove_from_current_zone(self, drone: Drone) -> None:
        """Removes a drone from its current zone's occupancy tracking.

        Args:
            drone: The drone to remove from its current zone.
        """
        current_zone: Zone | None = drone.current_zone
        if current_zone is None:
            return
        if current_zone.name in self.zone_occupancy:
            self.zone_occupancy[current_zone.name].remove(drone)
            if not self.zone_occupancy[current_zone.name]:
                del self.zone_occupancy[current_zone.name]

    def _move_drone_to_zone(self, drone: Drone, next_zone: Zone) -> None:
        """Moves a drone to the next zone and updates all tracking state.

        Args:
            drone: The drone to move.
            next_zone: The zone to move the drone into.
        """
        drone.move(next_zone)
        self.zone_occupancy.setdefault(next_zone.name, []).append(drone)
        self.turn_output.append(f"{drone.drone_id}-{next_zone.name}")
        drone.path.popleft()

    def _move_drone_through_connection(
        self, drone: Drone, connection: Connection, next_zone: Zone
    ) -> None:
        """Places a drone in transit through
        a connection toward a restricted zone.

        Args:
            drone: The drone to place in transit.
            connection: The connection the drone is traversing.
            next_zone: The destination zone at the end of the connection.
        """
        self.connection_occupancy.setdefault(connection.id, []).append(drone)
        self.turn_output.append(f"{drone.drone_id}-{connection.id}")
        drone.current_connection = connection
        drone.in_transit = True
        drone.remaining_transit_turns = next_zone.zone_cost - 1

    def _find_drone_goal(self, drone: Drone) -> Zone:
        """Returns the end zone from the drone's current path.

        Args:
            drone: The drone whose path is checked for the end zone.

        Returns:
            The last zone in the drone's path.

        Raises:
            ValueError: If the last zone
            in the drone's path is not an end zone.
        """
        last_zone = drone.path[-1]
        if last_zone.zone_type == "end":
            return last_zone
        raise ValueError("[_find_drone_goal] Drone must contain an end zone.")

    def _full_zones(self) -> Set[str]:
        """Returns the set of zone names that are currently at full capacity.

        Returns:
            A set of zone names where the number of occupying drones has
            reached or exceeded the zone's maximum capacity.
        """
        full_zones: Set[str] = set()
        for zone_name, drones in self.zone_occupancy.items():
            zone: Zone = self.graph.zones[zone_name]
            if len(drones) >= zone.max_drones:
                full_zones.add(zone_name)
        return full_zones

    def _new_path_calculator(self, drone: Drone) -> List[Zone] | None:
        """Calculates an alternative path for a blocked drone.

        Args:
            drone: The drone that needs a new path.

        Returns:
            A list of zones representing
            the new path excluding the current zone,
            or None if no alternative path exists.

        Raises:
            ValueError: If the drone has no current zone or an empty path.
        """
        current_zone: Zone | None = drone.current_zone
        if not current_zone:
            raise ValueError("[_new_path_calculator] "
                             "Drone has no current zone.")
        if not drone.path:
            raise ValueError("[_new_path_calculator] Drone path is empty")
        goal: Zone = self._find_drone_goal(drone)
        full_zones: Set[str] = self._full_zones()
        full_zones.discard(current_zone.name)
        new_path = path_finder(self.graph, current_zone,
                               goal, full_zones=full_zones)
        if new_path is None or len(new_path) <= 1:
            return None
        return new_path[1:]

    def _path_cost(self, path: List[Zone]) -> int:
        """Calculates the total movement cost of a path.

        Args:
            path: A list of zones representing the path to evaluate.

        Returns:
            The sum of movement costs for all zones in the path.
        """
        cost: int = 0
        for zone in path:
            cost += zone.zone_cost
        return cost

    def _should_reroute_path(self, drone: Drone,
                             new_path: List[Zone] | None) -> bool:
        """Determines whether a drone
        should take a new path instead of waiting.

        Compares the cost of rerouting against the cost of waiting on the
        current path. Rerouting is preferred if it is equal or cheaper.

        Args:
            drone: The drone considering a reroute.
            new_path: The alternative path to evaluate, or None if no
                alternative exists.

        Returns:
            True if the drone should reroute, otherwise False.
        """
        if new_path is None:
            return False
        wait_cost: int = self._path_cost(list(drone.path)) + 1
        reroute_cost: int = self._path_cost(new_path)
        return reroute_cost < wait_cost

    def _reroute_drone(self, drone: Drone,
                       new_path: List[Zone] | None) -> None:
        """Replaces a drone's current path with a new one.

        Args:
            drone: The drone to reroute.
            new_path: The new list of zones for the drone to follow.
        """
        if new_path is None:
            return
        drone.path.clear()
        drone.path.extend(new_path)

    def _handle_blocked_drone(self, drone: Drone) -> None:
        """Attempts to reroute a drone that cannot proceed on its current path.

        Calculates an alternative path and r eroutes the drone if the
        alternative is equal or cheaper than waiting.

        Args:
            drone: The drone that is blocked.
        """
        new_path: List[Zone] | None = self._new_path_calculator(drone)
        if self._should_reroute_path(drone, new_path):
            self._reroute_drone(drone, new_path)

    def _get_transit_connection(self, drone: Drone) -> Connection:
        """Returns the connection a drone is currently traversing.

        Args:
            drone: The drone in transit.

        Returns:
            The connection the drone is currently traversing.

        Raises:
            ValueError: If the drone has no current connection.
        """
        connection: Connection | None = drone.current_connection
        if connection is None:
            raise ValueError(
                "[_get_transit_connection] "
                f"missing connection for {drone.drone_id}"
            )
        return connection

    def _get_transit_destination(self, drone: Drone,
                                 connection: Connection) -> Zone:
        """Returns the destination zone of a drone currently in transit.

        Args:
            drone: The drone in transit.
            connection: The connection the drone is traversing.

        Returns:
            The zone at the other end of the connection from the drone's
            current position.
        """
        return (
            connection.zone2
            if drone.current_zone == connection.zone1
            else connection.zone1
        )

    def _release_connection(self, drone: Drone,
                            connection: Connection) -> None:
        """Removes a drone from a connection's occupancy tracking.

        Args:
            drone: The drone to release from the connection.
            connection: The connection to release the drone from.
        """
        self.connection_occupancy[connection.id].remove(drone)
        if not self.connection_occupancy[connection.id]:
            del self.connection_occupancy[connection.id]

    def _release_arrival_reservation(self, zone: Zone,
                                     arrival_turn: int) -> None:
        """Releases a previously reserved arrival slot for a drone at a zone.

        Args:
            zone: The zone where the arrival was reserved.
            arrival_turn: The turn number for which the arrival was reserved.
        """
        if arrival_turn not in self.zone_arrival_reservations:
            return
        if zone.name not in self.zone_arrival_reservations[arrival_turn]:
            return
        self.zone_arrival_reservations[arrival_turn][zone.name] -= 1
        if self.zone_arrival_reservations[arrival_turn][zone.name] == 0:
            del self.zone_arrival_reservations[arrival_turn][zone.name]
        if not self.zone_arrival_reservations[arrival_turn]:
            del self.zone_arrival_reservations[arrival_turn]

    def _clear_transit_state(self,
                             drone: Drone) -> None:
        """Resets all transit-related state
        on a drone after it completes transit.

        Args:
            drone: The drone whose transit state should be cleared.
        """
        drone.in_transit = False
        drone.current_connection = None
        drone.remaining_transit_turns = 0

    def _process_transit_drone(self, drone: Drone) -> None:
        """Advances a drone that is currently in transit through a connection.

        Decrements the remaining transit turns and, if transit is complete,
        releases the connection and moves the drone to its destination zone.

        Args:
            drone: The drone currently in transit.
        """
        connection: Connection = self._get_transit_connection(drone)
        drone.remaining_transit_turns -= 1
        if drone.remaining_transit_turns > 0:
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
        """Attempts to move a drone to its next zone via a connection.

        Handles both single-turn and multi-turn movements, checking connection
        and zone capacity before committing to the move. Reroutes the drone
        if capacity constraints cannot be met.

        Args:
            drone: The drone to move.
            connection: The connection the drone will traverse.
            next_zone: The destination zone.
        """
        if not self._has_connection_capacity(connection):
            self._handle_blocked_drone(drone)
            return

        if next_zone.zone_cost > 1:
            arrival_turn: int = self._arrival_turn(next_zone)
            if not self._has_arrival_capacity(next_zone, arrival_turn):
                self._handle_blocked_drone(drone)
                return
            self._reserve_arrival(next_zone, arrival_turn)
            self._reserve_connection(connection)
            self._remove_from_current_zone(drone)
            self._move_drone_through_connection(drone, connection, next_zone)
        else:
            if self._is_zone_at_capacity(next_zone):
                self._handle_blocked_drone(drone)
                return
            self._reserve_connection(connection)
            self._remove_from_current_zone(drone)
            self._move_drone_to_zone(drone, next_zone)

    def _arrival_turn(self, next_zone: Zone) -> int:
        """Calculates the turn number on which a drone will arrive at a zone.

        Args:
            next_zone: The destination zone.

        Returns:
            The turn number when the drone will arrive, based on the zone's
            movement cost.
        """
        return self.turns + next_zone.zone_cost - 1

    def _reserved_arrivals(self, zone: Zone,
                           arrival_turn: int) -> int:
        """Returns the number of drones already reserved
        to arrive at a zone on a given turn.

        Args:
            zone: The zone to check.
            arrival_turn: The turn number to check reservations for.

        Returns:
            The number of drones reserved
            to arrive at the zone on that turn.
        """
        return self.zone_arrival_reservations.get(arrival_turn,
                                                  {}).get(zone.name, 0)

    def _reserve_arrival(self, zone: Zone, arrival_turn: int) -> None:
        """Reserves an arrival slot for a drone at a zone on a future turn.

        Args:
            zone: The zone to reserve an arrival slot for.
            arrival_turn: The turn number to reserve the arrival on.
        """
        self.zone_arrival_reservations.setdefault(arrival_turn, {})
        self.zone_arrival_reservations[arrival_turn][zone.name] = (
            self.zone_arrival_reservations[arrival_turn].get(zone.name, 0) + 1
        )

    def _has_arrival_capacity(self, zone: Zone, arrival_turn: int) -> bool:
        """Checks whether a zone has capacity
        for an additional arrival on a given turn.

        Takes into account both current
        occupancy and already reserved arrivals.
        The end zone is never considered at capacity.

        Args:
            zone: The zone to check.
            arrival_turn: The turn number to check capacity for.

        Returns:
            True if the zone can accept another
            arrival on that turn, otherwise False.
        """
        if zone.zone_type == "end":
            return True
        current_occupancy: int = len(self.zone_occupancy.get(zone.name, []))
        reserved_occupancy: int = self._reserved_arrivals(zone, arrival_turn)
        return current_occupancy + reserved_occupancy < zone.max_drones

    def _colorize(self, text: str, color: str) -> str:
        """Wraps a string in ANSI escape codes to display it in a given color.

        Args:
            text: The string to colorize.
            color: The color name to apply, matched against the RGB color map.

        Returns:
            The colorized string if the color is recognized, otherwise the
            original string unchanged.
        """
        rgb = self.RGB_COLOR_MAP.get(color)
        if rgb is None:
            return text
        red, green, blue = rgb
        return f"\033[38;2;{red};{green};{blue}m{text}{self.ANSI_RESET}"

    def _format_move(self, move: str) -> str:
        """Formats a move string with its corresponding ANSI color.

        Args:
            move: A move string in 'D<ID>-<location>' format.

        Returns:
            The move string wrapped in ANSI color codes based on the
            destination zone or connection color.
        """
        _, location = move.split("-", 1)
        if location in self.graph.zones:
            zone = self.graph.zones[location]
            return self._colorize(move, zone.color)
        if location in self.graph.connections:
            connection = self.graph.connections[location]
            return self._colorize(move, connection.zone2.color)
        return move

    def _has_connection_capacity(self, connection: Connection) -> bool:
        """Checks whether a connection has
        capacity for an additional drone this turn.

        Args:
            connection: The connection to check.

        Returns:
            True if the connection has not yet
            reached its maximum link capacity
            for the current turn, otherwise False.
        """
        used = self.turn_connection_usage.get(connection.id, 0)
        return used < connection.max_link_capacity

    def _reserve_connection(self, connection: Connection) -> None:
        """Increments the usage count of a connection for the current turn.

        Args:
            connection: The connection to reserve capacity on.
        """
        self.turn_connection_usage[connection.id] = (
            self.turn_connection_usage.get(connection.id, 0) + 1
        )

    def move_drones(self) -> None:
        """Processes all drone movements for the current simulation turn.

        Drones are processed in order of shortest remaining path first to
        prioritize drones closest to the goal. Handles transit drones,
        blocked drones, and normal movement.

        Raises:
            ValueError: If a drone has no current zone, no next zone, or no
                valid connection to its next zone.
        """
        self.turn_output = []
        self.turn_connection_usage = {}
        drones_ordered: List[Drone] = sorted(
            self.drones, key=lambda drone: len(drone.path)
        )
        for drone in drones_ordered:
            if not drone.path:
                continue
            if drone.in_transit:
                self._process_transit_drone(drone)
                continue
            current_zone: Zone | None = drone.current_zone
            if current_zone is None:
                raise ValueError("[move_drones] "
                                 f"{drone.drone_id} has no current zone.")
            next_zone: Zone = drone.path[0]
            if not next_zone:
                raise ValueError(f"[move_drones] "
                                 f"{drone.drone_id} has no next zone")
            connection: Connection | None = self.graph.find_connection_zones(
                current_zone, next_zone
            )
            if connection is None:
                raise ValueError(
                    "[move_drones] No connection found between "
                    f"{current_zone.name} and {next_zone.name}"
                )
            if next_zone.zone_type == "blocked":
                self._handle_blocked_drone(drone)
                continue
            self._process_move_drone(drone, connection, next_zone)

    def _all_at_goal(self, drones: List[Drone],
                     zones: Dict[str, Zone]) -> bool:
        """Checks whether all drones have reached the end zone.

        Args:
            drones: The list of drones to check.
            zones: The Dictionary of all zones in the graph.

        Returns:
            True if all drones are currently in the end zone, otherwise False.

        Raises:
            ValueError: If no end zone is found in the graph.
        """
        end_zone = None
        for zone in zones.values():
            if zone.zone_type == "end":
                end_zone = zone
                break
        if end_zone is None:
            raise ValueError("[_all_at_goal] "
                             "No end zone found")
        return all(drone.current_zone == end_zone for drone in drones)

    def output(self) -> None:
        """Prints the formatted drone movements
        for the current simulation turn.

        Skips output if no drones moved this turn. Optionally prints
        capacity information if enabled.
        """
        if not self.turn_output:
            return
        formatted_moves = [self._format_move(move)
                           for move in sorted(self.turn_output)]
        print(" ".join(formatted_moves))
        if self.capacity_info_enabled:
            self._print_capacity_info()

    def run(self) -> None:
        """Runs the full simulation until all drones reach the end zone.

        Initialises drone paths, then iterates turn by turn, moving drones
        and recording frames until all drones have arrived at the goal.
        """
        self._path_initialisor()
        self._record_frame()
        while not self._all_at_goal(self.drones, self.graph.zones):
            self.turns += 1
            self.turn_output = []
            self.move_drones()
            self._record_frame()
            self.output()


if __name__ == "__main__":
    pass
