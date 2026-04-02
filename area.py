from abc import ABC


class Zone(ABC):
    def __init__(self, current_drone: str) -> None:
        self.current_drone: str = current_drone
        self.xcoordinate:


class StartZone(zone):
    def __init__(self, drones: list) -> None:
        self.drones: list = drones


class EndZone(zone):
    def __init__(self, drones: list) -> None:
        self.drones: list = drones


class SpecialZone(Zone):
    def __init__(self, max_drones) -> None:
        self.max_drones: int = max_drones


class Connection:
    pass


def main() -> None:
    area = Zone("test")
    print(area.current_drone)


if __name__ == "__main__":
    main()
