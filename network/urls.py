from django.urls import path
from . import views


urlpatterns = [
    path("nodes/", views.nodes, name="nodes"),
    path("nodes/<int:node_id>/", views.delete_node, name="delete-node"),

    path("edges/", views.edges, name="edges"),
    path("edges/<int:edge_id>/", views.delete_edge, name="delete-edge"),

    path("routes/shortest/", views.shortest_route, name="shortest-route"),
    path("routes/history/", views.route_history, name="route-history"),
]