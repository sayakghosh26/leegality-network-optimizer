import heapq

from decimal import Decimal

from network.models import Edge


def find_shortest_route(source, destination):

    if source == destination:
        return [source], Decimal("0.000")

    # Step 1: Build the adjacency list
    adjacency = {}

    edges = Edge.objects.select_related(
        "source",
        "destination"
    )

    for edge in edges:
        source_name = edge.source.name
        destination_name = edge.destination.name

        if source_name not in adjacency:
            adjacency[source_name] = []

        adjacency[source_name].append(
            (destination_name, edge.latency)
        )

    # Step 2: Initialize distances and priority queue
    distances = {source: Decimal("0.000")}
    previous = {}

    priority_queue = [(Decimal("0.000"), source)]

    # Step 3: Process nodes
    while priority_queue:

        current_latency, current_node = heapq.heappop(
            priority_queue
        )

        # Ignore outdated entries
        if current_latency > distances[current_node]:
            continue

        # Stop when destination is reached
        if current_node == destination:
            break

        # Step 4: Explore neighboring nodes
        for neighbor, edge_latency in adjacency.get(
            current_node, []
        ):

            new_latency = current_latency + edge_latency

            if (
                neighbor not in distances
                or new_latency < distances[neighbor]
            ):
                distances[neighbor] = new_latency
                previous[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_latency, neighbor)
                )

    # Step 5: Check whether destination is reachable
    if destination not in distances:
        return None, None

    # Step 6: Reconstruct the shortest path
    path = []
    current_node = destination

    while current_node != source:
        path.append(current_node)
        current_node = previous[current_node]

    path.append(source)
    path.reverse()

    return path, distances[destination]
