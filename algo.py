from file_parser import parser
from area import Graph, Zone
from typing import List, Dict, Tuple 
from heapq import heappush, heappop
from random import choice


def bfs_path(graph: Graph, start: Zone, goal: Zone) -> list[Zone]:
    zone_type: Dict = {
        "start": 0,
        "end": 0,
        "normal": 0,
        "priority":1,
        "restricted": 2,
    }
    path: List = []
    came_from: Dict = {start.name: start}
    visited: Dict = {start.name: "visited"}
    queue = [(zone_type[start.zone_type], start)]
    while(queue):
        cost, current = heappop(queue)
        if current == goal:
            current2: Zone = current
            while current2 != start:
                path.append(current2)
                current2 = came_from[current2.name]
            path.append(start)
            return path[::-1]
        neighbours: List = graph.find_neighbours(current.name)
        for i in range(len(neighbours)):
            neighbour: Tuple[int, Zone] = (zone_type[neighbours[i].zone_type], neighbours[i])
            neighbour_name: str = neighbours[i].name
            if neighbour_name not in visited and neighbours[i].zone_type != "blocked":
                visited[neighbour_name] = "visited"
                came_from[neighbour_name] = current
                heappush(queue, neighbour) 
    



def main() -> None:
    map: Graph = parser("./maps/hard/03_ultimate_challenge.txt")
    start: Zone = map.zones['start']
    goal: Zone = map.zones['goal']
    print(bfs_path(map, start, goal))
     
    







if __name__ == "__main__":
    main()
