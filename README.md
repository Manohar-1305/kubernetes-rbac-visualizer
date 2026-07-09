# RBAC Visualizer

RBAC Visualizer is a Python-based web application that visualizes Kubernetes Role-Based Access Control (RBAC) relationships in an interactive graph.

The application runs inside a Kubernetes cluster, retrieves RBAC objects using the Kubernetes API, and displays relationships between Users, Groups, ServiceAccounts, Roles, ClusterRoles, RoleBindings, and ClusterRoleBindings.

---

## Features

* Visualize Kubernetes RBAC
* Interactive graph view
* View Roles and ClusterRoles
* View RoleBindings and ClusterRoleBindings
* View ServiceAccounts
* Display relationships between RBAC objects
* Lightweight Python backend
* HTML/JavaScript frontend
* Containerized using Docker

---

## Project Structure

```text
rbac-analyzer/
│
├── backend/
│   ├── main.py
│   ├── k8s.py
│   ├── graph.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── Dockerfile
├── deployment.yaml
├── service.yaml
├── serviceaccount.yaml
├── clusterrole.yaml
├── clusterrolebinding.yaml
└── README.md
```

---

## Prerequisites

* Docker
* Kubernetes Cluster
* kubectl
* Docker Registry (optional for remote deployment)

---

## Build Docker Image

```bash
docker build -t rbac-visualizer:1.0 .
```

---

## Push Docker Image

```bash
docker tag rbac-visualizer:1.0 <YOUR_REGISTRY>/rbac-visualizer:latest

docker push <YOUR_REGISTRY>/rbac-visualizer:latest
```

Update the image name inside `deployment.yaml`.

---

## Deploy to Kubernetes

```bash
kubectl apply -f serviceaccount.yaml

kubectl apply -f clusterrole.yaml

kubectl apply -f clusterrolebinding.yaml

kubectl apply -f deployment.yaml

kubectl apply -f service.yaml
```

---

## Verify

```bash
kubectl get pods

kubectl get svc

kubectl logs deployment/rbac-visualizer
```

---

## Local Development

Install dependencies.

```bash
cd backend

pip install -r requirements.txt
```

Run the application.

```bash
python main.py
```

Open the application.

```
http://localhost:8000
```

---

## API Endpoints

| Endpoint                   | Description              |
| -------------------------- | ------------------------ |
| `/`                        | Web UI                   |
| `/health`                  | Health Check             |
| `/api/summary`             | RBAC Summary             |
| `/api/roles`               | List Roles               |
| `/api/clusterroles`        | List ClusterRoles        |
| `/api/rolebindings`        | List RoleBindings        |
| `/api/clusterrolebindings` | List ClusterRoleBindings |
| `/api/serviceaccounts`     | List Service Accounts    |
| `/api/graph`               | Graph Data               |

---

## Kubernetes Permissions

The application requires read-only access to:

* Roles
* ClusterRoles
* RoleBindings
* ClusterRoleBindings
* ServiceAccounts
* Namespaces

No create, update, delete, or patch permissions are required.

---

## Technologies Used

* Python
* FastAPI
* Kubernetes Python Client
* Cytoscape.js
* Docker
* Kubernetes

---

## License

This project is intended for learning and demonstration purposes.
