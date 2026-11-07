from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from django.utils.dateparse import parse_date

from .models import Node, RouteHistory, Edge
from .serializers import (
    NodeSerializer,
    EdgeSerializer,
    ShortestRouteRequestSerializer,
    RouteHistorySerializer
)
from .services import find_shortest_route


@api_view(["GET", "POST"])
def nodes(request):
    if request.method == "POST":
        serializer = NodeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    queryset = Node.objects.all().order_by("id")
    serializer = NodeSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def edges(request):
    if request.method == "POST":
        serializer = EdgeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    queryset = Edge.objects.select_related(
        "source", "destination"
    ).order_by("id")

    serializer = EdgeSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def shortest_route(request):

    # Step 1: Validate request data
    serializer = ShortestRouteRequestSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    source = serializer.validated_data["source"]
    destination = serializer.validated_data["destination"]

    # Step 2: Check whether source and destination exist
    source_exists = Node.objects.filter(name=source).exists()
    destination_exists = Node.objects.filter(name=destination).exists()

    if not source_exists or not destination_exists:
        return Response(
            {"error": "Source or destination node does not exist."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 3: Find the shortest route
    path, total_latency = find_shortest_route(
        source,
        destination
    )

    # Step 4: Check whether a route exists
    if path is None:
        return Response(
            {"error": "No route exists between the given nodes."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Step 5: Save successful route in history
    RouteHistory.objects.create(
        source=source,
        destination=destination,
        total_latency=total_latency,
        path=path
    )

    # Step 6: Return the result
    return Response(
        {
            "total_latency": total_latency,
            "path": path
        },
        status=status.HTTP_200_OK
    )


@api_view(["GET"])
def route_history(request):

    # Step 1: Get all route history records
    queryset = RouteHistory.objects.all()

    # Step 2: Filter by source
    source = request.query_params.get("source")

    if source:
        queryset = queryset.filter(source=source)

    # Step 3: Filter by destination
    destination = request.query_params.get("destination")

    if destination:
        queryset = queryset.filter(destination=destination)

    # Step 4: Validate and apply date_from
    date_from = request.query_params.get("date_from")

    parsed_date_from = None

    if date_from:
        parsed_date_from = parse_date(date_from)

        if parsed_date_from is None:
            return Response(
                {"error": "Invalid date_from format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = queryset.filter(
            created_at__date__gte=parsed_date_from
        )

    # Step 5: Validate and apply date_to
    date_to = request.query_params.get("date_to")

    parsed_date_to = None

    if date_to:
        parsed_date_to = parse_date(date_to)

        if parsed_date_to is None:
            return Response(
                {"error": "Invalid date_to format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = queryset.filter(
            created_at__date__lte=parsed_date_to
        )

    # Step 6: Validate date range
    if (
        parsed_date_from
        and parsed_date_to
        and parsed_date_from > parsed_date_to
    ):
        return Response(
            {"error": "date_from cannot be later than date_to."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 7: Order newest records first
    queryset = queryset.order_by("-created_at", "-id")

    # Step 8: Apply limit
    limit = request.query_params.get("limit")

    if limit is not None:
        try:
            limit = int(limit)

            if limit <= 0:
                raise ValueError

        except (ValueError, TypeError):
            return Response(
                {"error": "Limit must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = queryset[:limit]

    # Step 9: Serialize and return results
    serializer = RouteHistorySerializer(queryset, many=True)

    return Response(
        serializer.data,
        status=status.HTTP_200_OK
    )


@api_view(["DELETE"])
def delete_node(request, node_id):
    try:
        node = Node.objects.get(id=node_id)
    except Node.DoesNotExist:
        return Response(
            {"error": "Node not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    node.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["DELETE"])
def delete_edge(request, edge_id):
    try:
        edge = Edge.objects.get(id=edge_id)
    except Edge.DoesNotExist:
        return Response(
            {"error": "Edge not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    edge.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
