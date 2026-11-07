import pytest
from decimal import Decimal

from network.models import Node, Edge
from network.services import find_shortest_route


@pytest.mark.django_db
def test_finds_lowest_latency_route():
    a = Node.objects.create(name="A")
    b = Node.objects.create(name="B")
    c = Node.objects.create(name="C")

    # Direct route has latency 10.
    Edge.objects.create(source=a, destination=c, latency=10)

    # Indirect route has latency 5.
    Edge.objects.create(source=a, destination=b, latency=2)
    Edge.objects.create(source=b, destination=c, latency=3)

    path, latency = find_shortest_route("A", "C")

    assert path == ["A", "B", "C"]
    assert latency == Decimal("5.000")


@pytest.mark.django_db
def test_graph_respects_edge_direction():
    a = Node.objects.create(name="A")
    b = Node.objects.create(name="B")

    Edge.objects.create(source=a, destination=b, latency=5)

    path, latency = find_shortest_route("B", "A")

    assert path is None
    assert latency is None


@pytest.mark.django_db
def test_algorithm_handles_cycles():
    a = Node.objects.create(name="A")
    b = Node.objects.create(name="B")
    c = Node.objects.create(name="C")

    Edge.objects.create(source=a, destination=b, latency=2)
    Edge.objects.create(source=b, destination=a, latency=1)
    Edge.objects.create(source=b, destination=c, latency=3)

    path, latency = find_shortest_route("A", "C")

    assert path == ["A", "B", "C"]
    assert latency == Decimal("5.000")
