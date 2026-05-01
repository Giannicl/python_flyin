*This project has been created as part of the 42 curriculum by glieuw-a.*

# Fly-in — Drone Routing Simulation

## Description

Fly-in is a turn-based drone routing simulation written in Python. The goal is to navigate a fleet of drones from a start zone to an end zone through a network of connected zones, minimizing the total number of simulation turns while respecting strict movement and capacity constraints.

The simulation models a weighted graph where zones have types (normal, restricted, priority, blocked), capacity limits, and colors. Connections between zones also have capacity limits. The pathfinding algorithm routes all drones simultaneously, handling conflicts, rerouting, and multi-turn transit through restricted zones.

## Instructions

### Requirements

- Python 3.10 or later
- pygame (for graphical visualization)

### Installation

```bash
make install
```

### Running the simulation

```bash
python main.py <map_file>
```

### Options

| Flag | Description |
|---|---|
| `--visual` | Opens a pygame graphical window after the terminal simulation |
| `--capacity-info` | Prints zone and connection capacity usage after each turn |

### Examples

```bash
python main.py maps/01_linear_path.txt
python main.py maps/02_capacity_hell.txt --visual
python main.py maps/03_ultimate_challenge.txt --capacity-info
```

### Makefile commands

```bash
make install                              # Install dependencies
make run MAP=01_linear_path.txt           # Run the simulation
make run-visual MAP=01_linear_path.txt    # Run with graphical visualization
make run-capacity MAP=01_linear_path.txt  # Run with capacity info
make run-all MAP=01_linear_path.txt       # Run with all options
make debug MAP=01_linear_path.txt         # Run in debug mode with pdb
make lint                                 # Run flake8 and mypy
make clean                                # Remove __pycache__ and .mypy_cache
```

## Algorithm Explanation

### Pathfinding

The core algorithm is **Dijkstra's shortest path**, implemented from scratch in `algo.py`. It computes the lowest-cost path from start to end, using zone movement costs as edge weights (normal/priority = 1 turn, restricted = 2 turns, blocked = inaccessible).

### Multi-drone scheduling

All drones are initialized with the same shortest path. During each turn, drones are processed in order of **shortest remaining path first**, giving priority to drones closest to the goal to maximize throughput.

### Capacity-aware conflict resolution

Before each move, the simulation checks:
- **Zone capacity** (`max_drones`): a drone cannot enter a full zone
- **Connection capacity** (`max_link_capacity`): a connection cannot be used by more drones than its limit per turn
- **Arrival reservations**: for restricted zones requiring 2 turns of transit, future arrivals are pre-reserved to prevent overbooking

### Rerouting

When a drone is blocked, it recalculates an alternative path using Dijkstra with currently full zones excluded. The drone reroutes if the alternative path cost is less than or equal to the cost of waiting on the current path (`reroute_cost <= wait_cost`).

### Multi-turn transit

Restricted zones cost 2 turns to enter. When a drone starts moving toward one, it enters the connection and stays in transit for 1 additional turn before arriving. During transit, the drone occupies the connection and cannot be redirected.

### Design decisions

- **Reactive rerouting** over proactive path splitting keeps the implementation simple and works well across all map types
- **Shortest-path-first processing order** prevents faster drones from being blocked by slower ones
- **Arrival reservations** prevent race conditions where multiple drones simultaneously commit to entering a full restricted zone

### Complexity

- Dijkstra per call: O((V + E) log V) where V = zones, E = connections
- Per turn: O(D × (V + E) log V) in the worst case where D = number of drones and every drone reroutes
- In practice, rerouting is rare and most turns run in O(D)

## Visual Representation

### Terminal output

Each turn prints all drone movements space-separated, color-coded using ANSI escape codes based on the destination zone's color metadata. This gives an immediate visual indication of which zone type each drone is entering.

Example:
```
D1-waypoint1 D2-waypoint1
D1-waypoint2 D2-waypoint2
D1-goal D2-goal
Completed in 3 turns.
```

### Graphical interface (--visual)

The `--visual` flag opens a pygame window after the simulation completes, replaying the recorded frames with smooth interpolated animation. Features:

- Zones rendered as colored circles matching their color metadata
- Connections rendered as gray lines
- Drones rendered as blue triangles with offset positioning when multiple drones share a location
- Smooth interpolation between frames for fluid movement visualization
- Keyboard controls:
  - `SPACE` — restart the replay
  - `P` — pause/unpause
  - `↑` / `↓` — increase/decrease playback speed

### Capacity info (--capacity-info)

The `--capacity-info` flag prints zone and connection occupancy after each turn:

```
start: 0/1 | waypoint1: 1/1 | goal: 0/1
start-waypoint1: 0/1 | waypoint1-goal: 0/1
```

## Performance Results

| Map | Drones | Target | Result |
|---|---|---|---|
| Linear path | 2 | ≤ 6 | ✅ 4 turns |
| Simple fork | 3 | ≤ 6 | ✅ 5 turns |
| Basic capacity | 4 | ≤ 8 | ✅ 6 turns |
| Dead end trap | 5 | ≤ 15 | ✅ 8 turns |
| Circular loop | 6 | ≤ 20 | ✅ 16 turns |
| Priority puzzle | 4 | ≤ 12 | ✅ 7 turns |
| Maze nightmare | 8 | ≤ 45 | ✅ 14 turns |
| Capacity hell | 12 | ≤ 60 | ✅ 18 turns |
| Ultimate challenge | 15 | ≤ 35 | ✅ 26 turns |
| The Impossible Dream | 25 | ≤ 45 | 65 turns |

## Resources

### References

- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python heapq documentation](https://docs.python.org/3/library/heapq.html)
- [Python collections.deque documentation](https://docs.python.org/3/library/collections.html#collections.deque)
- [pygame documentation](https://www.pygame.org/docs/)
- [Google Python Style Guide — Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/en/stable/)

### AI usage

Claude (Anthropic) was used to assist with the following parts of this project:

- **Theory**: AI was used to deepen understanding of Dijkstra's algorithm, heap-based priority queues, and graph traversal concepts
- **Refactor suggestions**: AI was consulted to identify improvements to method structure, error handling, and type safety
- **Design suggestions**: AI provided guidance on class responsibilities, capacity management strategies, and simulation architecture decisions