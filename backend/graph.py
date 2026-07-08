from typing import Dict, List


class RBACGraph:

    # -------------------------------------------------------
    # User Graph
    # -------------------------------------------------------

    @staticmethod
    def user(user: Dict):

        nodes = []
        edges = []

        user_id = f"user:{user['name']}"

        nodes.append(
            {
                "id": user_id,
                "label": user["name"],
                "type": "User"
            }
        )

        for rb in user.get("roleBindings", []):

            rb_id = f"rb:{rb['namespace']}:{rb['name']}"

            nodes.append(
                {
                    "id": rb_id,
                    "label": rb["name"],
                    "type": "RoleBinding"
                }
            )

            edges.append(
                {
                    "source": user_id,
                    "target": rb_id
                }
            )

            role_id = f"{rb['kind']}:{rb['role']}"

            nodes.append(
                {
                    "id": role_id,
                    "label": rb["role"],
                    "type": rb["kind"]
                }
            )

            edges.append(
                {
                    "source": rb_id,
                    "target": role_id
                }
            )

        for crb in user.get("clusterRoleBindings", []):

            crb_id = f"crb:{crb['name']}"

            nodes.append(
                {
                    "id": crb_id,
                    "label": crb["name"],
                    "type": "ClusterRoleBinding"
                }
            )

            edges.append(
                {
                    "source": user_id,
                    "target": crb_id
                }
            )

            role_id = f"ClusterRole:{crb['role']}"

            nodes.append(
                {
                    "id": role_id,
                    "label": crb["role"],
                    "type": "ClusterRole"
                }
            )

            edges.append(
                {
                    "source": crb_id,
                    "target": role_id
                }
            )

        return {
            "nodes": RBACGraph.unique(nodes),
            "edges": RBACGraph.unique(edges)
        }

    # -------------------------------------------------------
    # Service Account Graph
    # -------------------------------------------------------

    @staticmethod
    def service_account(name, namespace, rolebindings, clusterrolebindings):

        nodes = []
        edges = []

        sa_id = f"sa:{namespace}:{name}"

        nodes.append(
            {
                "id": sa_id,
                "label": name,
                "type": "ServiceAccount"
            }
        )

        for rb in rolebindings:

            for s in rb.get("subjects", []):

                if s["kind"] != "ServiceAccount":
                    continue

                if s["name"] != name:
                    continue

                if s.get("namespace", namespace) != namespace:
                    continue

                rb_id = f"rb:{rb['namespace']}:{rb['name']}"

                nodes.append(
                    {
                        "id": rb_id,
                        "label": rb["name"],
                        "type": "RoleBinding"
                    }
                )

                edges.append(
                    {
                        "source": sa_id,
                        "target": rb_id
                    }
                )

                role_id = f"{rb['kind']}:{rb['role']}"

                nodes.append(
                    {
                        "id": role_id,
                        "label": rb["role"],
                        "type": rb["kind"]
                    }
                )

                edges.append(
                    {
                        "source": rb_id,
                        "target": role_id
                    }
                )

        for crb in clusterrolebindings:

            for s in crb.get("subjects", []):

                if s["kind"] != "ServiceAccount":
                    continue

                if s["name"] != name:
                    continue

                if s.get("namespace", namespace) != namespace:
                    continue

                crb_id = f"crb:{crb['name']}"

                nodes.append(
                    {
                        "id": crb_id,
                        "label": crb["name"],
                        "type": "ClusterRoleBinding"
                    }
                )

                edges.append(
                    {
                        "source": sa_id,
                        "target": crb_id
                    }
                )

                role_id = f"ClusterRole:{crb['role']}"

                nodes.append(
                    {
                        "id": role_id,
                        "label": crb["role"],
                        "type": "ClusterRole"
                    }
                )

                edges.append(
                    {
                        "source": crb_id,
                        "target": role_id
                    }
                )

        return {
            "nodes": RBACGraph.unique(nodes),
            "edges": RBACGraph.unique(edges)
        }
    # -------------------------------------------------------
    # Role Graph
    # -------------------------------------------------------

    @staticmethod
    def role(role, rolebindings):

        nodes = []
        edges = []

        role_id = f"Role:{role['namespace']}:{role['name']}"

        nodes.append(
            {
                "id": role_id,
                "label": role["name"],
                "type": "Role"
            }
        )

        for rb in rolebindings:

            if rb["role"] != role["name"]:
                continue

            if rb["namespace"] != role["namespace"]:
                continue

            rb_id = f"rb:{rb['namespace']}:{rb['name']}"

            nodes.append(
                {
                    "id": rb_id,
                    "label": rb["name"],
                    "type": "RoleBinding"
                }
            )

            edges.append(
                {
                    "source": rb_id,
                    "target": role_id
                }
            )

            for s in rb.get("subjects", []):

                subject_id = f"{s['kind']}:{s['name']}"

                nodes.append(
                    {
                        "id": subject_id,
                        "label": s["name"],
                        "type": s["kind"]
                    }
                )

                edges.append(
                    {
                        "source": subject_id,
                        "target": rb_id
                    }
                )

        return {
            "nodes": RBACGraph.unique(nodes),
            "edges": RBACGraph.unique(edges)
        }

    # -------------------------------------------------------
    # ClusterRole Graph
    # -------------------------------------------------------

    @staticmethod
    def cluster_role(role, bindings):

        nodes = []
        edges = []

        role_id = f"ClusterRole:{role['name']}"

        nodes.append(
            {
                "id": role_id,
                "label": role["name"],
                "type": "ClusterRole"
            }
        )

        for crb in bindings:

            if crb["role"] != role["name"]:
                continue

            crb_id = f"crb:{crb['name']}"

            nodes.append(
                {
                    "id": crb_id,
                    "label": crb["name"],
                    "type": "ClusterRoleBinding"
                }
            )

            edges.append(
                {
                    "source": crb_id,
                    "target": role_id
                }
            )

            for s in crb.get("subjects", []):

                subject_id = f"{s['kind']}:{s['name']}"

                nodes.append(
                    {
                        "id": subject_id,
                        "label": s["name"],
                        "type": s["kind"]
                    }
                )

                edges.append(
                    {
                        "source": subject_id,
                        "target": crb_id
                    }
                )

        return {
            "nodes": RBACGraph.unique(nodes),
            "edges": RBACGraph.unique(edges)
        }
    # -------------------------------------------------------
    # Remove duplicates
    # -------------------------------------------------------

    @staticmethod
    def unique(items: List[Dict]):

        unique_items = []

        seen = set()

        for item in items:

            key = tuple(sorted(item.items()))

            if key in seen:
                continue

            seen.add(key)

            unique_items.append(item)

        return unique_items