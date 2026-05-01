from __future__ import annotations
from models import Graph
import pygame
from typing import List, Dict, Tuple


class Visualizer:
    """Handles the graphical visualization
     of the drone simulation using pygame.

    Attributes:
        graph: The navigation graph containing all zones and connections.
        frames: List of frame snapshots recording drone positions each turn.
        width: Width of the display window in pixels.
        height: Height of the display window in pixels.
        margin: Margin around the drawable area in pixels.
        screen: The pygame display surface.
        clock: The pygame clock for controlling frame rate.
        running: Whether the visualization loop is active.
        paused: Whether the visualization is currently paused.
        speed: Playback speed multiplier for frame interpolation.
    """

    RGB_COLOR_MAP: Dict[str, Tuple[int, int, int]] = {
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
        self.screen: pygame.Surface = pygame.display.set_mode(
            (self.width, self.height))
        pygame.display.set_caption("Fly-in Drone Simulation")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = True
        self.paused: bool = False
        self.speed: float = 1.5

    def _coordinate_boundaries(self) -> Tuple[int, int, int, int]:
        """Returns the minimum and maximum x
        and y coordinates across all zones.

        Returns:
            A tuple of (min_x, max_x, min_y, max_y).
        """
        min_x: int = min(zone.xaxis for zone in self.graph.zones.values())
        max_x: int = max(zone.xaxis for zone in self.graph.zones.values())
        min_y: int = min(zone.yaxis for zone in self.graph.zones.values())
        max_y: int = max(zone.yaxis for zone in self.graph.zones.values())
        return min_x, max_x, min_y, max_y

    def _drawable_area(self) -> Tuple[int, int]:
        """Returns the width and height of the drawable area excluding margins.

        Returns:
            A tuple of (drawable_width, drawable_height) in pixels.
        """
        return self.width - 2 * self.margin, self.height - 2 * self.margin

    def _scale(self, range_x: int, range_y: int) -> float:
        """Calculates the scaling factor to fit the graph
        within the drawable area.

        Args:
            range_x: The range of x coordinates across all zones.
            range_y: The range of y coordinates across all zones.

        Returns:
            The scaling factor as a float.
        """
        drawable_width, drawable_height = self._drawable_area()
        scale_x: float = drawable_width / max(range_x, 1)
        scale_y: float = drawable_height / max(range_y, 1)
        return min(scale_x, scale_y)

    def _scaled_position(self, x: int, y: int) -> Tuple[int, int]:
        """Converts graph coordinates to screen pixel coordinates.

        Args:
            x: The x coordinate in graph space.
            y: The y coordinate in graph space.

        Returns:
            A tuple of (screen_x, screen_y) in pixels.
        """
        min_x, max_x, min_y, max_y = self._coordinate_boundaries()
        range_x: int = max_x - min_x
        range_y: int = max_y - min_y
        scale: float = self._scale(range_x, range_y)
        screen_x: int = int(self.margin + (x - min_x) * scale)
        screen_y: int = int(self.margin + (y - min_y) * scale)
        return screen_x, screen_y

    def _draw_connections(self) -> None:
        """Draws all connections between zones as lines on the screen."""
        for connection in self.graph.connections.values():
            x1, y1 = self._scaled_position(
                connection.zone1.xaxis, connection.zone1.yaxis
            )
            x2, y2 = self._scaled_position(
                connection.zone2.xaxis, connection.zone2.yaxis
            )
            pygame.draw.line(self.screen, (180, 180, 180),
                             (x1, y1), (x2, y2), 2)

    def _draw_drone_marker(self, x: int, y: int) -> None:
        """Draws a triangular drone marker at the given screen position.

        Args:
            x: The x screen coordinate of the marker.
            y: The y screen coordinate of the marker.
        """
        points: list[tuple[int, int]] = [
            (x + 9, y),
            (x - 7, y - 7),
            (x - 7, y + 7),
        ]
        pygame.draw.polygon(self.screen, (0, 0, 255), points)

    def _draw_zones(self) -> None:
        """Draws all zones as colored circles on the screen."""
        for zone in self.graph.zones.values():
            x, y = self._scaled_position(zone.xaxis, zone.yaxis)
            color = self.RGB_COLOR_MAP.get(zone.color, (120, 120, 120))

            pygame.draw.circle(self.screen, color, (x, y), 10)
            pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 18, 2)

    def _get_position(self,
                      location: str) -> Tuple[int, int]:
        """Returns the screen coordinates
        for a given zone or connection location.

        Args:
            location: A zone name or connection ID to look up.

        Returns:
            A tuple of (x, y) screen coordinates. Returns (0, 0) if the
            location is not found.
        """
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
        frame_a: Dict[str, str],
        frame_b: Dict[str, str],
        progress: float,
    ) -> None:
        """Draws all drones at interpolated positions between two frames.

        Args:
            frame_a: The current frame mapping
            drone IDs to their locations.
            frame_b: The next frame mapping
            drone IDs to their locations.
            progress: A float between 0.0 and 1.0 representing how far along
                the transition between frames the animation currently is.
        """

        grouped: Dict[str, list[str]] = {}

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

    def _handle_events(self) -> Dict[str, bool]:
        """Processes pygame events
        and returns a Dictionary of triggered commands.

        Returns:
            A Dictionary mapping command names to booleans indicating whether
            each command was triggered this frame. Commands include 'restart',
            'pause', 'speed_up', 'slow_down', and 'quit'.
        """
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

    def _update_progress(self, progress: float,
                         speed: float) -> float:
        """Updates the animation progress
        based on elapsed time and playback speed.

        Args:
            progress: The current animation progress between 0.0 and 1.0.
            speed: The current playback speed multiplier.

        Returns:
            The updated progress value.
        """
        time = self.clock.tick(60) / 1000
        return progress + time * speed

    def _draw_frame(self, frame_index: int,
                    progress: float) -> None:
        """Draws a single animation frame
        including connections, zones, and drones.

        Args:
            frame_index: The index of the current frame in the frames list.
            progress: A float between 0.0
            and 1.0 representing the interpolation
                progress toward the next frame.
        """
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

    def _advance_frame(self, frame_index: int,
                       progress: float) -> Tuple[int, float]:
        """Advances the current frame index
        when the animation progress is complete.

        Args:
            frame_index: The current frame index.
            progress: The current animation progress between 0.0 and 1.0.

        Returns:
            A tuple of (frame_index, progress) with the updated values.
        """
        if progress < 1.0:
            return frame_index, progress
        progress = 0.0
        if frame_index < len(self.frames) - 2:
            frame_index += 1
        elif self.frames:
            frame_index = len(self.frames) - 1
        return frame_index, progress

    def run(self) -> None:
        """Runs the pygame visualization loop until the window is closed.

        Handles user input, updates animation progress, and renders frames
        until the running flag is set to False.
        """
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
                progress = self._update_progress(progress,
                                                 self.speed)
                frame_index, progress = self._advance_frame(frame_index,
                                                            progress)
            self._draw_frame(frame_index, progress)
        pygame.quit()
