from django.urls import path
from . import views


urlpatterns = [
    path("nodes/", views.create_node, name="create-node"),
    path("edges/", views.create_edge, name="create-edge"),
]