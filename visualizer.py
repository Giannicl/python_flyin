from models import Graph
from simulation import Simulation
import pygame
from typing import List, Dict, Tuple


class Visualizer:
    RGB_COLOR_MAP: dict[str, tuple[int, int, int]] = {
        "red": (220, 50, 50),
        "green": (50, 180, 90),
        "blue": (50, 100, 220),
        "yellow": (220, 200, 50),
        "magenta": (200, 50, 200),
        "cyan": (50, 200, 200),
        "white": (240, 240, 240),
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
        "none": (120, 120, 120),
    }

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
        self.paused: bool = False
        self.speed: float = 1.5

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
            x1, y1 = self._scaled_position(
                connection.zone1.xaxis, connection.zone1.yaxis
            )
            x2, y2 = self._scaled_position(
                connection.zone2.xaxis, connection.zone2.yaxis
            )
            pygame.draw.line(self.screen, (180, 180, 180), (x1, y1), (x2, y2), 2)

    def _draw_drone_marker(self, x: int, y: int) -> None:
        points: list[tuple[int, int]] = [
            (x + 9, y),
            (x - 7, y - 7),
            (x - 7, y + 7),
        ]
        pygame.draw.polygon(self.screen, (0, 0, 255), points)

    def _draw_drone_at_zone(
        self,
        drone_id: str,
        zone_name: str,
        index: int = 0,
    ) -> None:
        zone = self.graph.zones[zone_name]
        x, y = self._scaled_position(zone.xaxis, zone.yaxis)
        offset = 10
        x += (index % 3 - 1) * offset
        y += (index // 3) * offset
        self._draw_drone_marker(x, y)

    def _draw_zones(self) -> None:
        for zone in self.graph.zones.values():
            x, y = self._scaled_position(zone.xaxis, zone.yaxis)
            color = self.RGB_COLOR_MAP.get(zone.color, (120, 120, 120))

            pygame.draw.circle(self.screen, color, (x, y), 10)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 18, 2)

    def _draw_drone_on_connection(
        self,
        drone_id: str,
        connection_id: str,
        index: int = 0,
    ) -> None:
        connection = self.graph.connections[connection_id]

        x1, y1 = self._scaled_position(connection.zone1.xaxis, connection.zone1.yaxis)
        x2, y2 = self._scaled_position(connection.zone2.xaxis, connection.zone2.yaxis)

        mid_x: int = (x1 + x2) // 2
        mid_y: int = (y1 + y2) // 2

        offset = 10
        mid_x += (index % 3 - 1) * offset
        mid_y += (index // 3) * offset

        self._draw_drone_marker(mid_x, mid_y)

    def _get_position(self, location: str) -> tuple[int, int]:
        if location in self.graph.zones:
            zone = self.graph.zones[location]
            return self._scaled_position(zone.xaxis, zone.yaxis)
        elif location in self.graph.connections:
            connection = self.graph.connections[location]
            x1, y1 = self._scaled_position(
                connection.zone1.xaxis, connection.zone1.yaxis
            )
            x2, y2 = self._scaled_position(
                connection.zone2.xaxis, connection.zone2.yaxis
            )
            return (x1 + x2) // 2, (y1 + y2) // 2
        return (0, 0)

    def _draw_drones_interpolated(
            self,
            frame_a: dict[str, str],
            frame_b: dict[str, str],
            progress: float,
        ) -> None:
            grouped: dict[str, list[str]] = {}
        
            for drone_id, location in frame_a.items():
                grouped.setdefault(location, []).append(drone_id)
        
            for location, drone_ids in grouped.items():
                for index, drone_id in enumerate(drone_ids):
                    loc_a = frame_a[drone_id]
                    loc_b = frame_b.get(drone_id, loc_a)
        
                    x1, y1 = self._get_position(loc_a)
                    x2, y2 = self._get_position(loc_b)
        
                    x = int(x1 + (x2 - x1) * progress)
                    y = int(y1 + (y2 - y1) * progress)
        
                    offset = 15
                    x += (index % 3 - 1) * offset
                    y += (index // 3) * offset
        
                    self._draw_drone_marker(x, y)

    def _handle_events(self) -> dict[str, bool]:
        commands = {
            "restart": False,
            "pause": False,
            "speed_up": False,
            "slow_down": False,
            "quit": False,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                commands["quit"] = True
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    commands["restart"] = True
                elif event.key == pygame.K_p:
                    commands["pause"] = True
                elif event.key == pygame.K_UP:
                    commands["speed_up"] = True
                elif event.key == pygame.K_DOWN:
                    commands["slow_down"] = True

        return commands
    def _update_progress(self, progress: float, speed: float) -> float:
        time = self.clock.tick(60) / 1000
        return progress + time * speed
    
    
    def _draw_frame(self, frame_index: int, progress: float) -> None:
        self.screen.fill((245, 245, 245))
        self._draw_connections()
        self._draw_zones()
    
        if self.frames:
            if frame_index < len(self.frames) - 1:
                self._draw_drones_interpolated(
                    self.frames[frame_index],
                    self.frames[frame_index + 1],
                    progress,
                )
            else:
                self._draw_drones_interpolated(
                    self.frames[frame_index],
                    self.frames[frame_index],
                    0.0,
                )
    
        pygame.display.flip()
    
    
    def _advance_frame(self, frame_index: int, progress: float) -> tuple[int, float]:
        if progress < 1.0:
            return frame_index, progress 
        progress = 0.0 
        if frame_index < len(self.frames) - 2:
            frame_index += 1
        elif self.frames:
            frame_index = len(self.frames) - 1 
        return frame_index, progress
    
    def run(self) -> None:
        frame_index: int = 0
        progress: float = 0.0
    
        while self.running:
            commands = self._handle_events() 
            if commands["restart"]:
                frame_index = 0
                progress = 0.0
            if commands["pause"]:
                self.paused = not self.paused
            if commands["speed_up"]:
                self.speed *= 1.2
            if commands["slow_down"]:
                self.speed *= 0.8
            if not self.paused:
                progress = self._update_progress(progress, self.speed)
                frame_index, progress = self._advance_frame(frame_index, progress)
            self._draw_frame(frame_index, progress)
        pygame.quit()
