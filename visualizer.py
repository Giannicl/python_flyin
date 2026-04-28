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

    def _draw_drone_marker(self, x: int, y: int) -> None:
        points: list[tuple[int, int]] = [
            (x + 9, y),
            (x - 7, y - 7),
            (x - 7, y + 7),
        ]
        pygame.draw.polygon(self.screen, (200, 0, 0), points)
    
    
    def _draw_drone_at_zone(self, drone_id: str, zone_name: str) -> None:
        zone = self.graph.zones[zone_name]
        x, y = self._scaled_position(zone.xaxis, zone.yaxis)
        self._draw_drone_marker(x, y)
    
    
    def _draw_drone_on_connection(self, drone_id: str, connection_id: str) -> None:
        connection = self.graph.connections[connection_id]
    
        x1, y1 = self._scaled_position(connection.zone1.xaxis, connection.zone1.yaxis)
        x2, y2 = self._scaled_position(connection.zone2.xaxis, connection.zone2.yaxis)
    
        mid_x: int = (x1 + x2) // 2
        mid_y: int = (y1 + y2) // 2
    
        self._draw_drone_marker(mid_x, mid_y)
    
    
    def _get_position(self, location: str) -> tuple[int, int]:
        if location in self.graph.zones:
            zone = self.graph.zones[location]
            return self._scaled_position(zone.xaxis, zone.yaxis)
    
        elif location in self.graph.connections:
            connection = self.graph.connections[location]
    
            x1, y1 = self._scaled_position(connection.zone1.xaxis, connection.zone1.yaxis)
            x2, y2 = self._scaled_position(connection.zone2.xaxis, connection.zone2.yaxis)
    
            return (x1 + x2) // 2, (y1 + y2) // 2
    
        return (0, 0)

    def _draw_drones_interpolated(
        self,
        frame_a: dict[str, str],
        frame_b: dict[str, str],
        progress: float
    ) -> None:
        for drone_id in frame_a:
            loc_a = frame_a[drone_id]
            loc_b = frame_b.get(drone_id, loc_a)
    
            x1, y1 = self._get_position(loc_a)
            x2, y2 = self._get_position(loc_b)
    
            x = int(x1 + (x2 - x1) * progress)
            y = int(y1 + (y2 - y1) * progress)
    
            self._draw_drone_marker(x, y)


    def run(self) -> None:
        frame_index: int = 0
        progress: float = 0.0
        speed: float = 1.5 
        while self.running:
            time = self.clock.tick(60) / 1000 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False    
            progress += time * speed
            self.screen.fill((245, 245, 245))
            self._draw_connections()
            self._draw_zones()
            if len(self.frames) > 1 and frame_index < len(self.frames) - 1:
                self._draw_drones_interpolated(
                    self.frames[frame_index],
                    self.frames[frame_index + 1],
                    progress
                )
            pygame.display.flip()
            if progress >= 1.0:
                progress = 0.0
                frame_index += 1
    
        pygame.quit()
