
import pytest

from rest_framework.test import APIClient

from network.models import Node, Edge


@pytest.mark.django_db
class TestNodeAPI:

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/nodes/"

    def test_create_node(self):
        response = self.client.post(
            self.url,
            {"name": "ServerA"},
            format="json"
        )

        assert response.status_code == 201
        assert response.data["name"] == "ServerA"
        assert Node.objects.filter(name="ServerA").exists()

    def test_create_node_without_name(self):
        response = self.client.post(
            self.url,
            {},
            format="json"
        )

        assert response.status_code == 400

    def test_create_duplicate_node(self):
        Node.objects.create(name="ServerA")

        response = self.client.post(
            self.url,
            {"name": "ServerA"},
            format="json"
        )

        assert response.status_code == 400


@pytest.mark.django_db
class TestEdgeAPI:

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/edges/"

        self.source = Node.objects.create(name="ServerA")
        self.destination = Node.objects.create(name="ServerB")

    def test_create_edge(self):
        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "ServerB",
                "latency": 12.5
            },
            format="json"
        )

        assert response.status_code == 201
        assert response.data["source"] == "ServerA"
        assert response.data["destination"] == "ServerB"
        assert Edge.objects.count() == 1

    def test_create_edge_with_nonexistent_source(self):
        response = self.client.post(
            self.url,
            {
                "source": "UnknownServer",
                "destination": "ServerB",
                "latency": 12.5
            },
            format="json"
        )

        assert response.status_code == 400

    def test_create_edge_with_nonexistent_destination(self):
        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "UnknownServer",
                "latency": 12.5
            },
            format="json"
        )

        assert response.status_code == 400

    @pytest.mark.parametrize("latency", [0, -1, -12.5])
    def test_create_edge_with_invalid_latency(self, latency):
        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "ServerB",
                "latency": latency
            },
            format="json"
        )

        assert response.status_code == 400

    def test_create_duplicate_edge(self):
        Edge.objects.create(
            source=self.source,
            destination=self.destination,
            latency=12.5
        )

        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "ServerB",
                "latency": 15.0
            },
            format="json"
        )

        assert response.status_code == 400
