
import pytest

from rest_framework.test import APIClient

from network.models import Node, Edge, RouteHistory

from decimal import Decimal


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


@pytest.mark.django_db
class TestShortestRouteAPI:

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/routes/shortest/"

        self.a = Node.objects.create(name="ServerA")
        self.b = Node.objects.create(name="ServerB")
        self.c = Node.objects.create(name="ServerC")
        self.d = Node.objects.create(name="ServerD")

    def test_find_shortest_route(self):
        Edge.objects.create(
            source=self.a,
            destination=self.b,
            latency=5
        )

        Edge.objects.create(
            source=self.a,
            destination=self.c,
            latency=2
        )

        Edge.objects.create(
            source=self.c,
            destination=self.b,
            latency=1
        )

        Edge.objects.create(
            source=self.b,
            destination=self.d,
            latency=4
        )

        Edge.objects.create(
            source=self.c,
            destination=self.d,
            latency=10
        )

        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "ServerD"
            },
            format="json"
        )

        assert response.status_code == 200
        assert response.data["path"] == [
            "ServerA",
            "ServerC",
            "ServerB",
            "ServerD"
        ]
        assert response.data["total_latency"] == Decimal("7.000")

    def test_no_route_exists(self):
        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "ServerD"
            },
            format="json"
        )

        assert response.status_code == 404

    def test_nonexistent_source(self):
        response = self.client.post(
            self.url,
            {
                "source": "UnknownServer",
                "destination": "ServerD"
            },
            format="json"
        )

        assert response.status_code == 400

    def test_nonexistent_destination(self):
        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "UnknownServer"
            },
            format="json"
        )

        assert response.status_code == 400

    def test_missing_source(self):
        response = self.client.post(
            self.url,
            {
                "destination": "ServerD"
            },
            format="json"
        )

        assert response.status_code == 400

    def test_missing_destination(self):
        response = self.client.post(
            self.url,
            {
                "source": "ServerA"
            },
            format="json"
        )

        assert response.status_code == 400

    def test_source_and_destination_are_same(self):
        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "ServerA"
            },
            format="json"
        )

        assert response.status_code == 200
        assert response.data["path"] == ["ServerA"]
        assert response.data["total_latency"] == Decimal("0.000")

    def test_successful_route_is_saved_in_history(self):
        Edge.objects.create(
            source=self.a,
            destination=self.b,
            latency=5
        )

        response = self.client.post(
            self.url,
            {
                "source": "ServerA",
                "destination": "ServerB"
            },
            format="json"
        )

        assert response.status_code == 200

        history = RouteHistory.objects.get(
            source="ServerA",
            destination="ServerB"
        )

        assert history.path == ["ServerA", "ServerB"]
        assert history.total_latency == Decimal("5.000")
