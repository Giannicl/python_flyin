from models import Graph
from simulation import Simulation
import pygame 
from typing import List, Dict

class Visualizer:
    def __init__(self, graph: Graph, frames: List[Dict[str, str]]) -> None:
        pygame.init()
        self.graph: Graph = graph
        self.frames: list[Dict[str, str]] = frames
        self.width: int = 1000
        self.height: int = 700
        self.margin: int = 80
        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in Drone Simulation")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True


    def _record_frames(self) -> None:
        frame: Dict[str, str] = {}



    def run(self) -> None:
        while self.running:
            for event in pygame.event.Event:
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((245, 245, 245))
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()


        

