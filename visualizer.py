from models import Graph
from simulation import Simulation
import pygame 
from typing import List, Dict, Tuple

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


    def _coordinate_boundaries(self) -> tuple[int, int, int, int]:
        min_x: int = min(zone.xaxis for zone in self.graph.zones.values())
        max_x: int = max(zone.xaxis for zone in self.graph.zones.values())
        min_y: int = min(zone.yaxis for zone in self.graph.zones.values())
        max_y: int = max(zone.yaxis for zone in self.graph.zones.values())
        return min_x, max_x, min_y, max_y
    
    
    def _drawable_area(self) -> tuple[int, int]:
        return self.width - 2 * self.margin, self.height - 2 * self.margin
    
    
    def _scale(self, range_x: int, range_y: int) -> float:
        drawable_width, drawable_height = self._drawable_area()
        scale_x: float = drawable_width / max(range_x, 1)
        scale_y: float = drawable_height / max(range_y, 1)
        return min(scale_x, scale_y)
    
    
    def _scaled_position(self, x: int, y: int) -> tuple[int, int]:
        min_x, max_x, min_y, max_y = self._coordinate_boundaries()
        range_x: int = max_x - min_x
        range_y: int = max_y - min_y
        scale: float = self._scale(range_x, range_y)
        screen_x: int = int(self.margin + (x - min_x) * scale)
        screen_y: int = int(self.margin + (y - min_y) * scale)
        return screen_x, screen_y

    def _draw_connections(self) -> None:
        for connection in self.graph.connections.values():
            x1, y1 = self._scaled_position(connection.zone1.xaxis, connection.zone1.yaxis)
            x2, y2 = self._scaled_position(connection.zone2.xaxis, connection.zone2.yaxis)
            pygame.draw.line(self.screen, (180, 180, 180), (x1, y1), (x2, y2), 2)

    def _draw_zones(self) -> None:
        for zone in self.graph.zones.values():
            x, y = self._scaled_position(zone.xaxis, zone.yaxis)
            pygame.draw.circle(self.screen, (60, 60, 60), (x, y), 10)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 18, 2)

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((245, 245, 245))
            self._draw_connections()
            self._draw_zones()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

