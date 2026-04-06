from area import Zone, Connection, Graph
from typing import Dict, List

def zone_initiator(line: str) -> Dict:
    elements: Dict = {}
    parts: List = line.split(' ', 4)
    elements['name'] = parts[1]
    elements['xaxis'] = int(parts[2])
    elements['yaxis'] = int(parts[3])
    meta_data: List = parts[4][1:-1].split(' ')
    if meta_data > 1:
        for i in range(len(meta_data)):
            parts: List = meta_data[i].split(' ')
            name: str = parts[0].split('=')
            data: int | str = int(parts.split[1]) if isinstance(parts[1], int) else parts[1]
            element[name] = data
    else:
        me
        name: str = meta_data[0]
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
                if "color" in zone_elements: 
                    zone: Zone = Zone(zone_elements['name'], zone_elements['xaxis'], zone_elements['yaxis'], color=zone_elements['color'])
                else:
                    zone: Zone = Zone(zone_elements['name'], zone_elements['xaxis'], zone_elements['yaxis'])

                graph.create_graph(zone)
            if "connection" in line:
                id += 1
                connection_elements: Dict = connection_initiator(line, id)
                name_zone1: str = connection_elements['zone1']
                name_zone2: str = connection_elements['zone2']
                connection = Connection(connection_elements['id'], graph.zones[name_zone1], graph.zones[name_zone2] )
                graph.create_graph(connection)

    print(graph.connections)
    return graph


if __name__ == "__main__":
    parser("./maps/easy/01_linear_path.txt")
