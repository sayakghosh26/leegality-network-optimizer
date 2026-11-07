from django.urls import path
from . import views


urlpatterns = [
    path("nodes/", views.nodes, name="nodes"),
    path("edges/", views.edges, name="edges"),
    path(
        "routes/shortest/",
        views.shortest_route,
        name="shortest-route"
    ),
    path(
        "routes/history/",
        views.route_history,
        name="route-history"
    ),
]