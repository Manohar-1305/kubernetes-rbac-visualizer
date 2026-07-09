from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from k8s import KubernetesRBAC
from graph import RBACGraph

# ---------------------------------------------------------
# FastAPI
# ---------------------------------------------------------

app = FastAPI(
    title="Kubernetes RBAC Visualizer",
    version="2.0.0"
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

FRONTEND_DIR = BASE_DIR.parent / "frontend"

STATIC_DIR = FRONTEND_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# ---------------------------------------------------------
# Kubernetes
# ---------------------------------------------------------

k8s = KubernetesRBAC()

# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
def health():

    return {
        "status": "ok"
    }

# ---------------------------------------------------------
# Summary
# ---------------------------------------------------------

@app.get("/api/summary")
def summary():

    return {
        "users": len(k8s.get_users()),
        "groups": len(k8s.get_groups()),
        "serviceAccounts": len(k8s.get_service_accounts()),
        "roles": len(k8s.get_roles()),
        "clusterRoles": len(k8s.get_cluster_roles()),
        "roleBindings": len(k8s.get_role_bindings()),
        "clusterRoleBindings": len(k8s.get_cluster_role_bindings())
    }

# ---------------------------------------------------------
# List APIs
# ---------------------------------------------------------

@app.get("/api/users")
def users():

    return k8s.get_users()


@app.get("/api/groups")
def groups():

    return k8s.get_groups()


@app.get("/api/serviceaccounts")
def service_accounts():

    return k8s.get_service_accounts()


@app.get("/api/roles")
def roles():

    return k8s.get_roles()


@app.get("/api/clusterroles")
def cluster_roles():

    return k8s.get_cluster_roles()


@app.get("/api/rolebindings")
def role_bindings():

    return k8s.get_role_bindings()


@app.get("/api/clusterrolebindings")
def cluster_role_bindings():

    return k8s.get_cluster_role_bindings()
# ---------------------------------------------------------
# User Details
# ---------------------------------------------------------

@app.get("/api/user/{name}")
def user(name: str):

    user = k8s.get_user(name)

    if user is None:

        return {
            "error": "User not found"
        }

    return {
        "details": user,
        "graph": RBACGraph.user(user)
    }


# ---------------------------------------------------------
# Group Details
# ---------------------------------------------------------

@app.get("/api/group/{name}")
def group(name: str):

    group = k8s.get_group(name)

    if group is None:

        return {
            "error": "Group not found"
        }

    return {
    "details": group,
    "graph": {
        "nodes": [],
        "edges": []
    }
}


# ---------------------------------------------------------
# Service Account Details
# ---------------------------------------------------------

@app.get("/api/serviceaccount/{namespace}/{name}")
def service_account(namespace: str, name: str):

    service_account = k8s.get_service_account(
        namespace,
        name
    )

    if service_account is None:

        return {
            "error": "ServiceAccount not found"
        }

    return {
        "details": service_account,
        "graph": RBACGraph.service_account(
            name,
            namespace,
            k8s.get_role_bindings(),
            k8s.get_cluster_role_bindings()
        )
    }


# ---------------------------------------------------------
# Role Details
# ---------------------------------------------------------

@app.get("/api/role/{namespace}/{name}")
def role(namespace: str, name: str):

    role = k8s.get_role(
        namespace,
        name
    )

    if role is None:

        return {
            "error": "Role not found"
        }

    return {
        "details": role,
        "graph": RBACGraph.role(
            role,
            k8s.get_role_bindings()
        )
    }


# ---------------------------------------------------------
# ClusterRole Details
# ---------------------------------------------------------

@app.get("/api/clusterrole/{name}")
def cluster_role(name: str):

    role = k8s.get_cluster_role_details(name)

    if role is None:

        return {
            "error": "ClusterRole not found"
        }

    return {
        "details": role,
        "graph": RBACGraph.cluster_role(
            role,
            k8s.get_cluster_role_bindings()
        )
    }
    # ---------------------------------------------------------
# Graph APIs
# ---------------------------------------------------------

@app.get("/api/graph/user/{name}")
def graph_user(name: str):

    user = k8s.get_user(name)

    if user is None:

        return {
            "error": "User not found"
        }

    return RBACGraph.user(user)


@app.get("/api/graph/serviceaccount/{namespace}/{name}")
def graph_service_account(namespace: str, name: str):

    service_account = k8s.get_service_account(
        namespace,
        name
    )

    if service_account is None:

        return {
            "error": "ServiceAccount not found"
        }

    return RBACGraph.service_account(
        name,
        namespace,
        k8s.get_role_bindings(),
        k8s.get_cluster_role_bindings()
    )


@app.get("/api/graph/role/{namespace}/{name}")
def graph_role(namespace: str, name: str):

    role = k8s.get_role(
        namespace,
        name
    )

    if role is None:

        return {
            "error": "Role not found"
        }

    return RBACGraph.role(
        role,
        k8s.get_role_bindings()
    )


@app.get("/api/graph/clusterrole/{name}")
def graph_cluster_role(name: str):

    role = k8s.get_cluster_role_details(name)

    if role is None:

        return {
            "error": "ClusterRole not found"
        }

    return RBACGraph.cluster_role(
        role,
        k8s.get_cluster_role_bindings()
    )


# ---------------------------------------------------------
# Frontend
# ---------------------------------------------------------

@app.get("/")
def index():

    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ---------------------------------------------------------
# Run
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
