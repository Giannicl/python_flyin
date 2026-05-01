from models import Graph, Zone
from typing import List, Dict, Tuple, Set
from heapq import heappush, heappop


def _reconstruct_path(
    came_from: Dict[str, Zone], start: Zone, goal: Zone
) -> List[Zone]:
    """Reconstructs the path from start to goal using the came_from map.

    Args:
        came_from: Dictionary mapping each zone name to the zone it was
            reached from during pathfinding.
        start: The starting zone.
        goal: The destination zone.

    Returns:
        An ordered list of zones from start to goal.
    """
    path: List[Zone] = []
    current: Zone = goal
    while current != start:
        path.append(current)
        current = came_from[current.name]
    path.append(start)
    return path[::-1]


def _valid_next_zone(
    neighbour_zone: Zone,
    goal: Zone,
    visited: Set[str],
    full_zones: Set[str],
    best_cost: Dict[str, int],
    new_total_cost: int,
) -> bool:
    """Checks whether a neighbouring zone is a valid next step in pathfinding.

    Args:
        neighbour_zone: The zone to evaluate.
        goal: The destination zone.
        visited: Set of already visited zone names.
        full_zones: Set of zone names that are at full capacity.
        best_cost: Dictionary mapping zone names
        to their current best known cost.
        new_total_cost: The cost to reach
        the neighbour zone via the current path.

    Returns:
        True if the zone is a valid next step, otherwise False.
    """
    neighbour_name: str = neighbour_zone.name
    return (
        neighbour_name not in visited
        and neighbour_zone.zone_type != "blocked"
        and (neighbour_name not in full_zones or neighbour_name == goal.name)
        and (
            neighbour_name not in best_cost
            or new_total_cost < best_cost[neighbour_name]
        )
    )


def _initialise_finder(
    start: Zone, full_zones: set[str] | None
) -> (Tuple[Dict[str, int], Dict[str, Zone],
            Set[str], Set[str],
            List[Tuple[int, Zone]]]):
    """Initialises the data structures needed for the pathfinding algorithm.

    Args:
        start: The starting zone.
        full_zones: Set of zone names that are at full capacity, or None.

    Returns:
        A tuple containing:
            - best_cost: Dictionary mapping zone names
            to their best known cost.
            - came_from: Dictionary mapping zone names
            to their predecessor zone.
            - visited: Empty set for tracking visited zones.
            - full_zones: Initialised set of full zone names.
            - queue: Priority queue initialised with the start zone.
    """
    best_cost: Dict[str, int] = {start.name: 0}
    came_from: Dict[str, Zone] = {start.name: start}
    visited: Set[str] = set()
    if full_zones is None:
        full_zones = set()
    queue: list[tuple[int, Zone]] = [(0, start)]
    return best_cost, came_from, visited, full_zones, queue


def path_finder(
    graph: Graph, start: Zone, goal: Zone, full_zones: set[str] | None = None
) -> list[Zone] | None:
    """Finds the lowest cost path from start to goal
        using Dijkstra's algorithm.

        Args:
            graph: The navigation graph containing zones and connections.
            start: The starting zone.
            goal: The destination zone.
            full_zones: Optional set of zone names currently at full capacity
                that should be avoided. Defaults to None.

        Returns:
            An ordered list of zones from start to goal if a path exists,
            otherwise None.
    """
    best_cost, came_from, visited, full_zones, queue = _initialise_finder(
        start, full_zones
    )
    if full_zones is None:
        full_zones = set()
    queue = [(0, start)]
    while queue:
        total_cost, current = heappop(queue)
        if current.name in visited:
            continue
        visited.add(current.name)
        if current == goal:
            return _reconstruct_path(came_from, start, goal)
        neighbours: List[Zone] = graph.find_neighbours(current.name)
        for neighbour_zone in neighbours:
            new_total_cost: int = total_cost + neighbour_zone.zone_cost
            if _valid_next_zone(
                neighbour_zone, goal, visited,
                full_zones, best_cost, new_total_cost
            ):
                best_cost[neighbour_zone.name] = new_total_cost
                came_from[neighbour_zone.name] = current
                heappush(queue, (new_total_cost, neighbour_zone))
    return None
