from file_parser import parser
from models import Graph, Zone
from typing import List, Dict, Tuple, Set 
from heapq import heappush, heappop
from random import choice


def _zone_cost(zone: Zone) -> int:
    cost_zone_type: Dict = {
        "start": 0,
        "end": 0,
        "normal": 0,
        "priority":1,
        "restricted": 2,
    }
    return cost_zone_type.get(zone.zone_type, 0)

def _reconstruct_path(came_from: Dict[str, Zone], start: Zone, goal: Zone) -> List[Zone]:
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
    neighbour_name: str = neighbour_zone.name
    return (
        neighbour_name not in visited
        and neighbour_zone.zone_type != "blocked"
        and (neighbour_name not in full_zones or neighbour_name == goal.name)
        and (neighbour_name not in best_cost or new_total_cost < best_cost[neighbour_name])
    )

def _initialise_finder(start: Zone, full_zones: set[str] | None) -> Tuple[Dict[str, int], Dict[str, Zone], Set[str], Set[str], List[Tuple[int, Zone]]]:
    best_cost: Dict[str, int] = {start.name: 0}
    came_from: Dict[str, Zone] = {start.name: start}
    visited: Set[str] = set()
    if full_zones is None:
        full_zones = set()
    queue: list[tuple[int, Zone]] = [(0, start)]
    return best_cost, came_from, visited, full_zones, queue

def path_finder(graph: Graph, start: Zone, goal: Zone, full_zones: set[str] | None = None) -> list[Zone] | None:
    best_cost, came_from, visited, full_zones, queue = _initialise_finder(start, full_zones)
    if full_zones is None:
        full_zones = set()
    queue = [(0, start)]
    while(queue):
        total_cost, current = heappop(queue)
        if current.name in visited:
            continue
        visited.add(current.name)
        if current == goal:
            return _reconstruct_path(came_from, start, goal)
        neighbours: List[Zone] = graph.find_neighbours(current.name)
        for neighbour_zone in neighbours:
            new_total_cost: int = total_cost + _zone_cost(neighbour_zone)
            if _valid_next_zone(neighbour_zone, goal, visited, full_zones, best_cost, new_total_cost):
                best_cost[neighbour_zone.name] = new_total_cost
                came_from[neighbour_zone.name] = current
                heappush(queue, (new_total_cost, neighbour_zone))
    return None
    



def main() -> None:
    map: Graph = parser("./maps/hard/03_ultimate_challenge.txt")
    start: Zone = map.zones['start']
    goal: Zone = map.zones['goal']
    print(bfs_path(map, start, goal))
     
    







if __name__ == "__main__":
    main()
