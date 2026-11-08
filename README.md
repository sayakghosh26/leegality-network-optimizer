# Network Route Optimization API

## Overview

This project implements a REST API for managing a network of servers and finding the shortest route between them based on network latency.

The network is represented as a directed, weighted graph:

- **Nodes** represent servers.
- **Edges** represent connections between servers.
- **Edge weights** represent network latency.

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
- Automated testing using Pytest and pytest-django.
- Continuous Integration using GitHub Actions.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.13+ | Programming language |
| Django | Backend web framework |
| Django REST Framework | REST API development |
| SQLite | Database |
| Pytest | Testing framework |
| pytest-django | Django integration for pytest |
| Git | Version control |
| GitHub Actions | Continuous Integration |

## Design Decisions

### 1. Directed Graph

The network is implemented as a directed graph.

An edge from `ServerA` to `ServerB` does not automatically create a connection from `ServerB` to `ServerA`.

Each connection can only be traversed in its defined direction.

### 2. Duplicate Prevention

- Node names must be unique.
- A source-destination pair can have only one edge.

These rules are enforced through serializer validation and database-level constraints.

### 3. Positive Latency

Every edge must have a latency greater than zero.

This is enforced through serializer validation and a database-level check constraint.

Positive latency is also a requirement for the Dijkstra implementation used by this application.

### 4. Route History

Successful shortest-route queries are stored in the database.

Route history stores source and destination names as strings rather than foreign keys. This ensures historical records remain available even if a node is deleted later.

### 5. Node Deletion

Deleting a node automatically deletes its connected edges through Django's `CASCADE` relationship.

Existing route history is preserved.

### 6. Decimal Latency

Latency values are stored using Django's `DecimalField` and calculated using Python's `Decimal` type to avoid common floating-point precision issues.

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
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

The application requires a Django secret key through an environment variable.

Generate a new secret key:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set the generated key in your PowerShell session:

```powershell
$env:DJANGO_SECRET_KEY="your-generated-secret-key"
```

Configure debug mode for local development:

```powershell
$env:DJANGO_DEBUG="true"
```

Optionally configure allowed hosts:

```powershell
$env:DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
```

These environment variables apply to the current PowerShell session. If you open a new terminal, configure them again.

**Important:** Do not commit real secret keys to the repository. For production deployments, use a securely generated secret key, set `DJANGO_DEBUG=false`, and configure `DJANGO_ALLOWED_HOSTS` with the actual application hostnames.

### 6. Apply Database Migrations

```powershell
python manage.py migrate
```

### 7. Start the Development Server

```powershell
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

API base URL:

```text
http://127.0.0.1:8000/api/
```

### 8. Run the Tests

```powershell
pytest -v
```

The test suite verifies models, serializers, API endpoints, validation, route-history filtering, and shortest-route calculation logic.

## API Documentation

**Base URL:**

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

- `400 Bad Request`: Missing, blank, or duplicate node name.

### 2. Get All Nodes

**Endpoint:** `GET /api/nodes/`

Returns all nodes in the network, ordered by ID.

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

- `400 Bad Request`: Missing source or destination.
- `400 Bad Request`: Source or destination node does not exist.
- `400 Bad Request`: Latency is zero or negative.
- `400 Bad Request`: Duplicate edge.

### 4. Get All Edges

**Endpoint:** `GET /api/edges/`

Returns all edges in the network, ordered by ID.

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
    "total_latency": "17.000",
    "path": [
        "ServerA",
        "ServerB",
        "ServerD"
    ]
}
```

The response above is an illustrative example.

**Possible Errors:**

- `400 Bad Request`: Missing or invalid source/destination.
- `400 Bad Request`: Source or destination node does not exist.
- `404 Not Found`: No route exists between the requested nodes.

Successful route queries are automatically stored in route history.

If the source and destination are the same existing node, the API returns that node as the path with a total latency of zero.

### 6. Get Route History

**Endpoint:** `GET /api/routes/history/`

Returns previously calculated successful routes.

**Optional Query Parameters:**

| Parameter | Description | Example |
|---|---|---|
| `source` | Filter by source node name | `source=ServerA` |
| `destination` | Filter by destination node name | `destination=ServerD` |
| `limit` | Maximum number of records to return | `limit=10` |
| `date_from` | Include records from this date onwards | `date_from=2026-01-01` |
| `date_to` | Include records up to this date | `date_to=2026-12-31` |

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
        "total_latency": "17.000",
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

- `400 Bad Request`: Invalid date format. Expected format is `YYYY-MM-DD`.
- `400 Bad Request`: `date_from` is later than `date_to`.
- `400 Bad Request`: Limit must be a positive integer.

### 7. Delete a Node

**Endpoint:** `DELETE /api/nodes/{node_id}/`

Deletes a node and its connected edges.

**Example Request:**

```text
DELETE /api/nodes/1/
```

**Successful Response:**

```text
204 No Content
```

**Possible Errors:**

- `404 Not Found`: Node does not exist.

Deleting a node does not delete existing route history.

### 8. Delete an Edge

**Endpoint:** `DELETE /api/edges/{edge_id}/`

Deletes a specific edge from the network.

**Example Request:**

```text
DELETE /api/edges/1/
```

**Successful Response:**

```text
204 No Content
```

**Possible Errors:**

- `404 Not Found`: Edge does not exist.

## Algorithm: Dijkstra's Shortest Path

The application uses Dijkstra's algorithm to find the route with the minimum total latency between two nodes in a directed, weighted graph.

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
- If no route exists, the API returns a `404 Not Found` response.
- If the source and destination are the same existing node, the route contains that node and the total latency is zero.

## Continuous Integration

The project uses GitHub Actions to automatically run the test suite.

The workflow is triggered when code is pushed to the `main` branch or when a pull request targets `main`.

The workflow performs the following steps:

1. Checks out the repository.
2. Sets up Python 3.13.
3. Installs project dependencies from `requirements.txt`.
4. Applies database migrations.
5. Runs the automated tests using Pytest.

The CI workflow uses a test-only Django secret key and does not require a production secret.

This helps ensure that changes do not break existing functionality.
