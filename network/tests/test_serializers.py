
import pytest

from network.models import Node, Edge
from network.serializers import NodeSerializer, EdgeSerializer


@pytest.mark.django_db
class TestNodeSerializer:

    def test_valid_node_data(self):
        serializer = NodeSerializer(data={"name": "ServerA"})

        assert serializer.is_valid()
        node = serializer.save()

        assert node.name == "ServerA"

    def test_missing_node_name(self):
        serializer = NodeSerializer(data={})

        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_duplicate_node_name(self):
        Node.objects.create(name="ServerA")

        serializer = NodeSerializer(data={"name": "ServerA"})

        assert not serializer.is_valid()
        assert "name" in serializer.errors


@pytest.mark.django_db
class TestEdgeSerializer:

    def setup_method(self):
        self.source = Node.objects.create(name="ServerA")
        self.destination = Node.objects.create(name="ServerB")

    def test_valid_edge_data(self):
        data = {
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 12.5
        }

        serializer = EdgeSerializer(data=data)

        assert serializer.is_valid(), serializer.errors

        edge = serializer.save()

        assert edge.source == self.source
        assert edge.destination == self.destination
        assert float(edge.latency) == 12.5

    def test_source_node_does_not_exist(self):
        data = {
            "source": "UnknownServer",
            "destination": "ServerB",
            "latency": 12.5
        }

        serializer = EdgeSerializer(data=data)

        assert not serializer.is_valid()
        assert "source" in serializer.errors

    def test_destination_node_does_not_exist(self):
        data = {
            "source": "ServerA",
            "destination": "UnknownServer",
            "latency": 12.5
        }

        serializer = EdgeSerializer(data=data)

        assert not serializer.is_valid()
        assert "destination" in serializer.errors

    @pytest.mark.parametrize("latency", [0, -1, -12.5])
    def test_invalid_latency(self, latency):
        data = {
            "source": "ServerA",
            "destination": "ServerB",
            "latency": latency
        }

        serializer = EdgeSerializer(data=data)

        assert not serializer.is_valid()
        assert "latency" in serializer.errors

    def test_duplicate_edge(self):
        Edge.objects.create(
            source=self.source,
            destination=self.destination,
            latency=12.5
        )

        data = {
            "source": "ServerA",
            "destination": "ServerB",
            "latency": 15.0
        }

        serializer = EdgeSerializer(data=data)

        assert not serializer.is_valid()
        assert "non_field_errors" in serializer.errors
