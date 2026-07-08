from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from k8s import KubernetesRBAC
from graph import RBACGraphBuilder

app = FastAPI(
    title="RBAC Visualizer",
    version="1.0.0"
)

# ------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# Frontend
# ------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# ------------------------------------------------------------------
# Kubernetes
# ------------------------------------------------------------------

k8s = KubernetesRBAC()

# ------------------------------------------------------------------
# Health
# ------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------

@app.get("/api/summary")
def summary():

    data = k8s.get_rbac_data()

    return {
        "roles": len(data["roles"]),
        "clusterRoles": len(data["cluster_roles"]),
        "roleBindings": len(data["role_bindings"]),
        "clusterRoleBindings": len(data["cluster_role_bindings"]),
        "serviceAccounts": len(data["service_accounts"]),
        "subjects": len(data["subjects"]),
    }

# ------------------------------------------------------------------
# Roles
# ------------------------------------------------------------------

@app.get("/api/roles")
def roles():

    result = []

    for role in k8s.get_roles():
        result.append(
            {
                "name": role.metadata.name,
                "namespace": role.metadata.namespace,
                "rules": [
                    {
                        "apiGroups": rule.api_groups,
                        "resources": rule.resources,
                        "verbs": rule.verbs,
                    }
                    for rule in (role.rules or [])
                ],
            }
        )

    return result

# ------------------------------------------------------------------
# ClusterRoles
# ------------------------------------------------------------------

@app.get("/api/clusterroles")
def cluster_roles():

    result = []

    for role in k8s.get_cluster_roles():
        result.append(
            {
                "name": role.metadata.name,
                "rules": [
                    {
                        "apiGroups": rule.api_groups,
                        "resources": rule.resources,
                        "verbs": rule.verbs,
                    }
                    for rule in (role.rules or [])
                ],
            }
        )

    return result

# ------------------------------------------------------------------
# RoleBindings
# ------------------------------------------------------------------

@app.get("/api/rolebindings")
def role_bindings():

    result = []

    for rb in k8s.get_role_bindings():
        result.append(
            {
                "name": rb.metadata.name,
                "namespace": rb.metadata.namespace,
                "roleRef": {
                    "kind": rb.role_ref.kind,
                    "name": rb.role_ref.name,
                },
                "subjects": [
                    {
                        "kind": s.kind,
                        "name": s.name,
                        "namespace": getattr(s, "namespace", None),
                    }
                    for s in (rb.subjects or [])
                ],
            }
        )

    return result

# ------------------------------------------------------------------
# ClusterRoleBindings
# ------------------------------------------------------------------

@app.get("/api/clusterrolebindings")
def cluster_role_bindings():

    result = []

    for crb in k8s.get_cluster_role_bindings():
        result.append(
            {
                "name": crb.metadata.name,
                "roleRef": {
                    "kind": crb.role_ref.kind,
                    "name": crb.role_ref.name,
                },
                "subjects": [
                    {
                        "kind": s.kind,
                        "name": s.name,
                        "namespace": getattr(s, "namespace", None),
                    }
                    for s in (crb.subjects or [])
                ],
            }
        )

    return result

# ------------------------------------------------------------------
# ServiceAccounts
# ------------------------------------------------------------------

@app.get("/api/serviceaccounts")
def service_accounts():

    result = []

    for sa in k8s.get_service_accounts():
        result.append(
            {
                "name": sa.metadata.name,
                "namespace": sa.metadata.namespace,
            }
        )

    return result

# ------------------------------------------------------------------
# Graph
# ------------------------------------------------------------------

@app.get("/api/graph")
def graph():

    data = k8s.get_rbac_data()

    graph = RBACGraphBuilder(data).build()

    return JSONResponse(content=graph.model_dump())

# ------------------------------------------------------------------
# Frontend
# ------------------------------------------------------------------

@app.get("/")
def index():
    return FileResponse(FRONTEND_DIR / "index.html")

# ------------------------------------------------------------------
# Run
# ------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )