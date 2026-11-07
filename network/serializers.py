
from rest_framework import serializers

from network.models import Node, Edge, RouteHistory


class NodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Node
        fields = ["id", "name"]


class EdgeSerializer(serializers.ModelSerializer):

    source = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Node.objects.all()
    )

    destination = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Node.objects.all()
    )

    class Meta:
        model = Edge
        fields = ["id", "source", "destination", "latency"]

    def validate_latency(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Latency must be greater than zero."
            )

        return value

    def validate(self, data):
        source = data.get("source")
        destination = data.get("destination")

        if source and destination:
            edge_exists = Edge.objects.filter(
                source=source,
                destination=destination
            ).exists()

            if edge_exists:
                raise serializers.ValidationError(
                    "An edge between these nodes already exists."
                )

        return data


class ShortestRouteRequestSerializer(serializers.Serializer):

    source = serializers.CharField(max_length=100)
    destination = serializers.CharField(max_length=100)


class RouteHistorySerializer(serializers.ModelSerializer):

    class Meta:
        model = RouteHistory
        fields = [
            "id",
            "source",
            "destination",
            "total_latency",
            "path",
            "created_at"
        ]