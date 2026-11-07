
import pytest

from rest_framework.test import APIClient

from network.models import Node, Edge, RouteHistory

from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone


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


@pytest.mark.django_db
class TestRouteHistoryAPI:

    def setup_method(self):
        self.client = APIClient()
        self.url = "/api/routes/history/"

        self.history1 = RouteHistory.objects.create(
            source="ServerA",
            destination="ServerB",
            total_latency=5,
            path=["ServerA", "ServerB"]
        )

        self.history2 = RouteHistory.objects.create(
            source="ServerA",
            destination="ServerC",
            total_latency=10,
            path=["ServerA", "ServerC"]
        )

        self.history3 = RouteHistory.objects.create(
            source="ServerB",
            destination="ServerD",
            total_latency=15,
            path=["ServerB", "ServerD"]
        )

    def test_get_all_route_history(self):
        response = self.client.get(self.url)

        assert response.status_code == 200
        assert len(response.data) == 3

    def test_filter_by_source(self):
        response = self.client.get(
            self.url,
            {"source": "ServerA"}
        )

        assert response.status_code == 200
        assert len(response.data) == 2

        for record in response.data:
            assert record["source"] == "ServerA"

    def test_filter_by_destination(self):
        response = self.client.get(
            self.url,
            {"destination": "ServerD"}
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["destination"] == "ServerD"

    def test_filter_by_source_and_destination(self):
        response = self.client.get(
            self.url,
            {
                "source": "ServerA",
                "destination": "ServerB"
            }
        )

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_limit_route_history(self):
        response = self.client.get(
            self.url,
            {"limit": 2}
        )

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_invalid_limit(self):
        response = self.client.get(
            self.url,
            {"limit": "invalid"}
        )

        assert response.status_code == 400

    def test_zero_limit(self):
        response = self.client.get(
            self.url,
            {"limit": 0}
        )

        assert response.status_code == 400

    def test_filter_by_date_from(self):
        yesterday = timezone.now() - timedelta(days=1)

        RouteHistory.objects.filter(
            id=self.history1.id
        ).update(created_at=yesterday)

        today = timezone.localdate()

        response = self.client.get(
            self.url,
            {"date_from": today.isoformat()}
        )

        assert response.status_code == 200
        assert len(response.data) == 2

    def test_filter_by_date_to(self):
        yesterday = timezone.now() - timedelta(days=1)

        RouteHistory.objects.filter(
            id=self.history1.id
        ).update(created_at=yesterday)

        today = timezone.localdate()

        response = self.client.get(
            self.url,
            {"date_to": yesterday.date().isoformat()}
        )

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_invalid_date_format(self):
        response = self.client.get(
            self.url,
            {"date_from": "not-a-date"}
        )

        assert response.status_code == 400

    def test_date_from_after_date_to(self):
        today = date.today()

        response = self.client.get(
            self.url,
            {
                "date_from": (today + timedelta(days=2)).isoformat(),
                "date_to": today.isoformat()
            }
        )

        assert response.status_code == 400

    def test_filter_by_date_range(self):
        yesterday = timezone.now() - timedelta(days=1)
        today = timezone.now()
        tomorrow = timezone.now() + timedelta(days=1)

        RouteHistory.objects.filter(
            id=self.history1.id
        ).update(created_at=yesterday)

        RouteHistory.objects.filter(
            id=self.history2.id
        ).update(created_at=today)

        RouteHistory.objects.filter(
            id=self.history3.id
        ).update(created_at=tomorrow)

        current_date = timezone.localdate().isoformat()

        response = self.client.get(
            self.url,
            {
                "date_from": current_date,
                "date_to": current_date
            }
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["id"] == self.history2.id

    def test_empty_route_history(self):
        RouteHistory.objects.all().delete()

        response = self.client.get(self.url)

        assert response.status_code == 200
        assert response.data == []


@pytest.mark.django_db
class TestNodeListAPI:
    url = "/api/nodes/"

    def test_get_all_nodes(self):
        Node.objects.create(name="ServerA")
        Node.objects.create(name="ServerB")

        response = APIClient().get(self.url)

        assert response.status_code == 200
        assert len(response.data) == 2
        assert response.data[0]["name"] == "ServerA"
        assert response.data[1]["name"] == "ServerB"

    def test_get_nodes_when_empty(self):
        response = APIClient().get(self.url)

        assert response.status_code == 200
        assert response.data == []


@pytest.mark.django_db
class TestEdgeListAPI:
    url = "/api/edges/"

    def test_get_all_edges(self):
        source = Node.objects.create(name="ServerA")
        destination = Node.objects.create(name="ServerB")

        Edge.objects.create(
            source=source,
            destination=destination,
            latency=12.5
        )

        response = APIClient().get(self.url)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["source"] == "ServerA"
        assert response.data[0]["destination"] == "ServerB"
        assert float(response.data[0]["latency"]) == 12.5

    def test_get_edges_when_empty(self):
        response = APIClient().get(self.url)

        assert response.status_code == 200
        assert response.data == []


@pytest.mark.django_db
class TestDeleteNodeAPI:
    def test_delete_node(self):
        node = Node.objects.create(name="ServerA")

        response = APIClient().delete(f"/api/nodes/{node.id}/")

        assert response.status_code == 204
        assert not Node.objects.filter(id=node.id).exists()

    def test_delete_node_cascades_edges(self):
        source = Node.objects.create(name="ServerA")
        destination = Node.objects.create(name="ServerB")

        edge = Edge.objects.create(
            source=source,
            destination=destination,
            latency=12.5
        )

        response = APIClient().delete(f"/api/nodes/{source.id}/")

        assert response.status_code == 204
        assert not Node.objects.filter(id=source.id).exists()
        assert not Edge.objects.filter(id=edge.id).exists()

    def test_delete_nonexistent_node(self):
        response = APIClient().delete("/api/nodes/9999/")

        assert response.status_code == 404


@pytest.mark.django_db
class TestDeleteEdgeAPI:
    def test_delete_edge(self):
        source = Node.objects.create(name="ServerA")
        destination = Node.objects.create(name="ServerB")

        edge = Edge.objects.create(
            source=source,
            destination=destination,
            latency=12.5
        )

        response = APIClient().delete(f"/api/edges/{edge.id}/")

        assert response.status_code == 204
        assert not Edge.objects.filter(id=edge.id).exists()

        # Nodes should remain unaffected.
        assert Node.objects.filter(id=source.id).exists()
        assert Node.objects.filter(id=destination.id).exists()

    def test_delete_nonexistent_edge(self):
        response = APIClient().delete("/api/edges/9999/")

        assert response.status_code == 404
