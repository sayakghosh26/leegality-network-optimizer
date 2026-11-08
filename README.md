# Network Route Optimization API

## Overview

This project implements a REST API for managing a network of servers and finding the shortest route between them based on network latency.

The network is represented as a directed weighted graph:

- Nodes represent servers.
- Edges represent connections between servers.
- Edge weights represent network latency.

The application uses Dijkstra's shortest-path algorithm to calculate the route with the minimum total latency between two servers.

The application is built using Python, Django, Django REST Framework, and SQLite.

## Features

- Create and manage network nodes.
- Create directed connections between nodes.
- Validate node names and edge details.
- Prevent duplicate nodes and edges.
- Calculate the shortest route using Dijkstra's algorithm.
- Return the minimum total latency and corresponding path.
- Store successful route queries in the database.
- Retrieve route history with optional filters.
- List all nodes and edges.
- Delete nodes and edges.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| Django | Backend web framework |
| Django REST Framework | REST API development |
| SQLite | Database |
| Pytest | Testing framework |
| pytest-django | Django integration for pytest |
| Git | Version control |

## Design Decisions

### Directed Graph

The network is implemented as a directed graph.

An edge from ServerA to ServerB does not automatically create a connection from ServerB to ServerA.

### Duplicate Prevention

Node names must be unique.

A source-destination pair can have only one edge.

### Positive Latency

Every edge must have a latency greater than zero.

This is enforced through serializer validation and database-level constraints.

### Route History

Successful shortest-route queries are stored in the database.

Route history stores source and destination names as strings so historical records remain available even if a node is deleted.

### Node Deletion

Deleting a node automatically deletes its connected edges through Django's CASCADE relationship.

Existing route history is preserved.

## Installation and Setup

### Prerequisites

Make sure you have the following installed:

- Python 3.13 or above
- Git
- pip

### 1. Clone the Repository

```bash
git clone https://github.com/sayakghosh26/leegality-network-optimizer.git
cd leegality-network-optimizer
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations

```bash
python manage.py migrate
```

### 6. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at:

http://127.0.0.1:8000/

### 7. Run the Tests

```bash
pytest -v
```

The test suite verifies models, serializers, API endpoints, and shortest-route calculation logic.

## API Documentation

Base URL:

```text
http://127.0.0.1:8000/api/
```

All request bodies should use JSON format.

### 1. Create a Node

**Endpoint:** `POST /api/nodes/`

Creates a new node in the network.

**Request Body:**

```json
{
    "name": "ServerA"
}
```

**Successful Response (201 Created):**

```json
{
    "id": 1,
    "name": "ServerA"
}
```

**Possible Errors:**

- 400 Bad Request: Missing node name or duplicate node name.

### 2. Get All Nodes

**Endpoint:** `GET /api/nodes/`

Returns all nodes in the network.

**Successful Response (200 OK):**

```json
[
    {
        "id": 1,
        "name": "ServerA"
    },
    {
        "id": 2,
        "name": "ServerB"
    }
]
```

Returns an empty array if no nodes exist.

### 3. Create an Edge

**Endpoint:** `POST /api/edges/`

Creates a directed connection between two existing nodes.

**Request Body:**

```json
{
    "source": "ServerA",
    "destination": "ServerB",
    "latency": 12.5
}
```

**Successful Response (201 Created):**

```json
{
    "id": 1,
    "source": "ServerA",
    "destination": "ServerB",
    "latency": "12.500"
}
```

**Possible Errors:**

- 400 Bad Request: Missing source or destination.
- 400 Bad Request: Source or destination node does not exist.
- 400 Bad Request: Latency is zero or negative.
- 400 Bad Request: Duplicate edge.

### 4. Get All Edges

**Endpoint:** `GET /api/edges/`

Returns all edges in the network.

**Successful Response (200 OK):**

```json
[
    {
        "id": 1,
        "source": "ServerA",
        "destination": "ServerB",
        "latency": "12.500"
    }
]
```

Returns an empty array if no edges exist.

### 5. Find the Shortest Route

**Endpoint:** `POST /api/routes/shortest/`

Calculates the route with the minimum total latency between two nodes using Dijkstra's algorithm.

**Request Body:**

```json
{
    "source": "ServerA",
    "destination": "ServerD"
}
```

**Successful Response (200 OK):**

```json
{
    "total_latency": "23.400",
    "path": [
        "ServerA",
        "ServerB",
        "ServerD"
    ]
}
```

The response above is an illustrative example.

**Possible Errors:**

- 400 Bad Request: Missing or invalid source/destination.
- 400 Bad Request: Source or destination node does not exist.
- 404 Not Found: No route exists between the requested nodes.

Successful route queries are automatically stored in route history.

### 6. Get Route History

**Endpoint:** `GET /api/routes/history/`

Returns previously calculated successful routes.

**Optional Query Parameters:**

| Parameter | Description | Example |
|---|---|---|
| source | Filter by source node name | `source=ServerA` |
| destination | Filter by destination node name | `destination=ServerD` |
| limit | Maximum number of records to return | `limit=10` |
| date_from | Filter records from this date | `date_from=2026-01-01` |
| date_to | Filter records up to this date | `date_to=2026-12-31` |

**Example Request:**

```text
GET /api/routes/history/?source=ServerA&destination=ServerD&limit=10
```

**Successful Response (200 OK):**

```json
[
    {
        "id": 1,
        "source": "ServerA",
        "destination": "ServerD",
        "total_latency": "23.400",
        "path": [
            "ServerA",
            "ServerB",
            "ServerD"
        ],
        "created_at": "2026-11-08T10:30:00Z"
    }
]
```

The response above is an illustrative example.

History records are returned with the newest records first.

**Possible Errors:**

- 400 Bad Request: Invalid date format.
- 400 Bad Request: Invalid date range.
- 400 Bad Request: Limit must be a positive integer.

### 7. Delete a Node

**Endpoint:** `DELETE /api/nodes/{node_id}/`

Deletes a node and its connected edges.

**Example:**

```text
DELETE /api/nodes/1/
```

**Successful Response:**

`204 No Content`

**Possible Errors:**

- 404 Not Found: Node does not exist.

Deleting a node does not delete existing route history.

### 8. Delete an Edge

**Endpoint:** `DELETE /api/edges/{edge_id}/`

Deletes a specific edge from the network.

**Example:**

```text
DELETE /api/edges/1/
```

**Successful Response:**

`204 No Content`

**Possible Errors:**

- 404 Not Found: Edge does not exist.

## Algorithm: Dijkstra's Shortest Path

The application uses Dijkstra's algorithm to find the route with the minimum total latency between two nodes in a directed weighted graph.

### How It Works

1. Build an adjacency list representing the network using the stored edges.
2. Initialize the source node's distance to zero.
3. Use a min-priority queue to process the node with the smallest known latency.
4. Visit its neighboring nodes and calculate their new cumulative latency.
5. Update a neighbor's distance if a shorter route is found.
6. Continue until the destination is reached or no more reachable nodes remain.
7. Reconstruct the shortest path using a predecessor mapping.

Python's `heapq` module is used to implement the min-priority queue.

### Example

Consider the following network:

```text
ServerA --10--> ServerB
ServerA --20--> ServerC
ServerB --5---> ServerC
ServerB --10--> ServerD
ServerC --2---> ServerD
```

There are multiple possible routes from ServerA to ServerD:

| Route | Total Latency |
|---|---:|
| ServerA → ServerB → ServerD | 20 |
| ServerA → ServerC → ServerD | 22 |
| ServerA → ServerB → ServerC → ServerD | 17 |

The algorithm selects:

```text
ServerA → ServerB → ServerC → ServerD
```

Total latency: `17`

### Time and Space Complexity

Let:

- V = Number of vertices (nodes).
- E = Number of edges (connections).

| Complexity | Value | Explanation |
|---|---|---|
| Time | O((V + E) log V) | Uses an adjacency list and a min-priority queue. |
| Space | O(V + E) | Stores the adjacency list, distances, predecessors, and priority queue. |

### Important Considerations

- Dijkstra's algorithm works with non-negative edge weights.
- This application enforces strictly positive edge latencies.
- The graph is directed, so connections are traversed only in their defined direction.
- If no route exists, the API returns a 404 response.
- If the source and destination are the same node, the route contains that node and the total latency is zero.