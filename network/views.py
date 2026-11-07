from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Node, RouteHistory
from .serializers import (
    NodeSerializer,
    EdgeSerializer,
    ShortestRouteRequestSerializer
)
from .services import find_shortest_route


@api_view(["POST"])
def create_node(request):
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


@api_view(["POST"])
def create_edge(request):
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
