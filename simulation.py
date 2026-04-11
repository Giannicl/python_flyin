from typing import Dict, List
from file_parser import parser
from models import Zone, Connection, Graph, Drone
from collections import deque
from algo import bfs_path

class Simulation:
    def __init__(self, drones: List[Drone], map: Graph) -> None:
        self.drones: List[Drone] = drones
        self.map: Graph = map
        self.drone_positions: Dict = {}
        self.zone_occupancy: Dict = {}
        self.current_turn: int = 0
        self.turns: int = 0

    def move_drones(self) -> None:
        for drone in self.drones:
            start_zone: Zone = drone.path[0]
            if len(drone.path) == 1:
                drone.path.popleft()
                continue
            next_zone: Zone = drone.path[1]
            drone.move(start_zone, next_zone)
            drone.path.popleft()

    def run(self) -> None:
        while(any(drone.path for drone in self.drones)):
            self.turns += 1
            self.move_drones()
            

if __name__ == "__main__":
    graph: Graph = parser("./maps/easy/01_linear_path.txt")
    drone: Drone = Drone("a")
    drone1 = Drone("b")
    drone.add_path(bfs_path(graph, graph.zones["start"], graph.zones["goal"]))
    drone1.add_path(bfs_path(graph, graph.zones["start"], graph.zones["goal"]))
    drones: list[Drone] = [drone, drone1] 
    sim = Simulation(drones, graph)
    sim.run()
    print(sim.turns)
    
