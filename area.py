from typing import Optional


class Zone:
    def __init__(
        self,
        name: str,
        xaxis: int,
        yaxis: int,
        zone_type: str = "normal",
        color: str = "none",
        max_drones: int = 1,
    ) -> None:
        self.name: str = name
        self.current_drone: Optional[str] = None
        self.xaxis: int = xaxis
        self.yaxis: int = yaxis
        self.zone_type: str = zone_type
        self.color: str = color
        self.max_drones: int = max_drones


class Connection:
    def __init__(self, zone1: Zone, zone2: Zone, max_links: int = 1) -> None:
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_links


def main() -> None:
    area = Zone("test", 2, 3)
    print(area.current_drone)
    print()


if __name__ == "__main__":
    main()
