from typing import List, Dict, Tuple, Set, Optional, Iterable
import itertools
from collections import defaultdict, Counter
import re
import sys
from queue import Queue


Graph = Dict[str, List[str]]
Wire = Tuple[str, str]


def parse_connections(lines: List[str]) -> Graph:
    graph = defaultdict(list)
    for line in lines:
        m = re.match(r'(\w+): (.+)', line)
        component, rest = m.groups()
        others = rest.split()
        graph[component].extend(others)
        for other in others:
            graph[other].append(component)
    return graph


def visit_connected_nodes_dfs(graph: Graph,
                              wires: Iterable[Wire],
                              node: str,
                              visited: Set[str]) -> None:
    visited.add(node)
    for other in graph[node]:
        conn = tuple(sorted((node, other)))
        if conn not in wires and other not in visited:
            visit_connected_nodes_dfs(graph, wires, other, visited)


def get_separated_pair(graph: Graph,
                       wires: Iterable[Wire]) -> Optional[Tuple[Set[str], Set[str]]]:
    nodes_left = set(graph.keys())
    groups = []
    while nodes_left:
        free_node = next(iter(nodes_left))
        visited = set()
        visit_connected_nodes_dfs(graph, wires, free_node, visited)
        nodes_left -= visited
        groups.append(visited)
        if len(groups) > 2:
            break
        if len(groups) == 2 and not nodes_left:
            return groups


def measure_connections_usage_bfs(graph: Graph,
                                  start_node: str,
                                  wires_counting: Dict[str, int]) -> None:
    visited = set()
    queue = Queue()
    queue.put((start_node, None))
    while not queue.empty():
        node, parent = queue.get()
        if node in visited:
            continue
        visited.add(node)
        if parent is not None:
            conn = tuple(sorted((parent, node)))
            wires_counting[conn] += 1
        for neigh in graph[node]:
            queue.put((neigh, node))


def map_connections_usage(graph: Graph) -> Dict[str, int]:
    wires_counting = Counter()
    for idx, node in enumerate(graph.keys()):
        if idx > 100:
            break
        measure_connections_usage_bfs(graph, node, wires_counting)
    return wires_counting


def find_separation(graph: Graph,
                    wires_connectivity: Dict[str, int]) -> Tuple[Set[str], Set[str]]:
    wires = sorted(wires_connectivity.items(), key=lambda w: w[1], reverse=True)
    for unplugged in itertools.combinations((wire for wire, _ in wires), 3):
        groups = get_separated_pair(graph, unplugged)
        if groups is not None:
            return groups[0], groups[1]


def resolve_part1(input):
    sys.setrecursionlimit(10000)
    graph = parse_connections(input)
    s1, s2 = find_separation(graph, map_connections_usage(graph))
    return len(s1) * len(s2)


def resolve_part2(input):
    return "Merry Christmas!"