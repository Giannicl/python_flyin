from area import Zone, Connection, Graph
from typing import Dict, List

def zone_initiator(line: str) -> Dict:
    elements: Dict = {}
    parts: List = line.split(" ")
    elements['name'] = parts[1]
    elements['xaxis'] = parts[2]
    elements['yaxis'] = parts[3]
    elements['color'] = parts[4].split("=")[1][:-1]
    return elements

def connection_initiator(line: str, id: int) -> Dict:
    elements: Dict = {}
    parts: List = line.split(' ')
    elements['id'] = id
    zone1, zone2 = parts[1].split('-')
    elements['zone1'] = zone1
    elements['zone2'] = zone2
    return elements



def parser(filename: str) -> list[Zone | Connection]:
    graph: Graph = Graph()
    id: int = 0
    with open(filename, "r") as file:
        for line in file:
            line: List = line.strip()
            if not line or line.startswith("#"):
                continue
            if "hub" in line:
                zone_elements: Dict = zone_initiator(line)
                zone: Zone = Zone(zone_elements['name'], zone_elements['xaxis'], zone_elements['yaxis'], zone_elements['color'])
                graph.create_graph(zone)
            if "connection" in line:
                id += 1
                connection_elements: Dict = connection_initiator(line, id)
                name_zone1: str = connection_elements['zone1']
                name_zone2: str = connection_elements['zone2']
                connection = Connection(connection_elements['id'], graph.zones[name_zone1], graph.zones[name_zone2] )
                graph.create_graph(connection) 
    return graph


if __name__ == "__main__":
    parser("./maps/easy/01_linear_path.txt")
