import pytest

from django.db import IntegrityError, transaction

from network.models import Node, Edge, RouteHistory


@pytest.mark.django_db
class TestNodeModel:

    def test_create_node(self):
        node = Node.objects.create(name="ServerA")

        assert node.id is not None
        assert node.name == "ServerA"

    def test_node_name_must_be_unique(self):
        Node.objects.create(name="ServerA")

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Node.objects.create(name="ServerA")


@pytest.mark.django_db
class TestEdgeModel:

    def test_create_edge(self):
        source = Node.objects.create(name="ServerA")
        destination = Node.objects.create(name="ServerB")

        edge = Edge.objects.create(
            source=source,
            destination=destination,
            latency=12.5
        )

        assert edge.id is not None
        assert edge.source == source
        assert edge.destination == destination
        assert float(edge.latency) == 12.5

    def test_duplicate_edge_not_allowed(self):
        source = Node.objects.create(name="ServerA")
        destination = Node.objects.create(name="ServerB")

        Edge.objects.create(
            source=source,
            destination=destination,
            latency=12.5
        )

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Edge.objects.create(
                    source=source,
                    destination=destination,
                    latency=15.0
                )

    @pytest.mark.parametrize("latency", [0, -1, -12.5])
    def test_latency_must_be_positive(self, latency):
        source = Node.objects.create(name="ServerA")
        destination = Node.objects.create(name="ServerB")

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Edge.objects.create(
                    source=source,
                    destination=destination,
                    latency=latency
                )


@pytest.mark.django_db
class TestRouteHistoryModel:

    def test_create_route_history(self):
        history = RouteHistory.objects.create(
            source="ServerA",
            destination="ServerD",
            total_latency=23.4,
            path=["ServerA", "ServerB", "ServerD"]
        )

        assert history.id is not None
        assert history.source == "ServerA"
        assert history.destination == "ServerD"
        assert history.path == [
            "ServerA",
            "ServerB",
            "ServerD"
        ]
        assert history.created_at is not None