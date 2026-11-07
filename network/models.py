from django.db import models
from django.db.models import Q


class Node(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Edge(models.Model):
    source = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="outgoing_edges"
    )
    destination = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="incoming_edges"
    )
    latency = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_source_destination"
            ),
            models.CheckConstraint(
                condition=Q(latency__gt=0),
                name="edge_latency_positive"
            ),
        ]

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class RouteHistory(models.Model):
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    total_latency = models.DecimalField(max_digits=12, decimal_places=3)
    path = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} -> {self.destination}"
