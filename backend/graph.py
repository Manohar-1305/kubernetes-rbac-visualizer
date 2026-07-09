from typing import Dict, List


class RBACGraph:

    # -------------------------------------------------------
    # Helpers
    # -------------------------------------------------------

    @staticmethod
    def _node(node_id, label, node_type):

        return {
            "id": node_id,
            "label": label,
            "type": node_type
        }

    @staticmethod
    def _edge(source, target):

        return {
            "source": source,
            "target": target
        }

    # -------------------------------------------------------
    # User Graph
    # -------------------------------------------------------

    @staticmethod
    def user(user: Dict):

        nodes = []
        edges = []

        user_id = f"user:{user['name']}"

        nodes.append(
            RBACGraph._node(
                user_id,
                user["name"],
                "User"
            )
        )

        for rb in user.get("roleBindings", []):

            rb_id = f"rb:{rb['namespace']}:{rb['name']}"

            nodes.append(
                RBACGraph._node(
                    rb_id,
                    rb["name"],
                    "RoleBinding"
                )
            )

            edges.append(
                RBACGraph._edge(
                    user_id,
                    rb_id
                )
            )

            role_id = f"{rb['kind']}:{rb['role']}"

            nodes.append(
                RBACGraph._node(
                    role_id,
                    rb["role"],
                    rb["kind"]
                )
            )

            edges.append(
                RBACGraph._edge(
                    rb_id,
                    role_id
                )
            )

        for crb in user.get("clusterRoleBindings", []):

            crb_id = f"crb:{crb['name']}"

            nodes.append(
                RBACGraph._node(
                    crb_id,
                    crb["name"],
                    "ClusterRoleBinding"
                )
            )

            edges.append(
                RBACGraph._edge(
                    user_id,
                    crb_id
                )
            )

            role_id = f"ClusterRole:{crb['role']}"

            nodes.append(
                RBACGraph._node(
                    role_id,
                    crb["role"],
                    "ClusterRole"
                )
            )

            edges.append(
                RBACGraph._edge(
                    crb_id,
                    role_id
                )
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
            RBACGraph._node(
                sa_id,
                name,
                "ServiceAccount"
            )
        )

        for rb in rolebindings:

            for subject in rb.get("subjects", []):

                if subject["kind"] != "ServiceAccount":
                    continue

                if subject["name"] != name:
                    continue

                if subject.get("namespace") != namespace:
                    continue

                rb_id = f"rb:{rb['namespace']}:{rb['name']}"

                nodes.append(
                    RBACGraph._node(
                        rb_id,
                        rb["name"],
                        "RoleBinding"
                    )
                )

                edges.append(
                    RBACGraph._edge(
                        sa_id,
                        rb_id
                    )
                )

                role_id = f"{rb['kind']}:{rb['role']}"

                nodes.append(
                    RBACGraph._node(
                        role_id,
                        rb["role"],
                        rb["kind"]
                    )
                )

                edges.append(
                    RBACGraph._edge(
                        rb_id,
                        role_id
                    )
                )

        for crb in clusterrolebindings:

            for subject in crb.get("subjects", []):

                if subject["kind"] != "ServiceAccount":
                    continue

                if subject["name"] != name:
                    continue

                if subject.get("namespace") != namespace:
                    continue

                crb_id = f"crb:{crb['name']}"

                nodes.append(
                    RBACGraph._node(
                        crb_id,
                        crb["name"],
                        "ClusterRoleBinding"
                    )
                )

                edges.append(
                    RBACGraph._edge(
                        sa_id,
                        crb_id
                    )
                )

                role_id = f"ClusterRole:{crb['role']}"

                nodes.append(
                    RBACGraph._node(
                        role_id,
                        crb["role"],
                        "ClusterRole"
                    )
                )

                edges.append(
                    RBACGraph._edge(
                        crb_id,
                        role_id
                    )
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
            RBACGraph._node(
                role_id,
                role["name"],
                "Role"
            )
        )

        for rb in rolebindings:

            if rb["kind"] != "Role":
                continue

            if rb["role"] != role["name"]:
                continue

            if rb["namespace"] != role["namespace"]:
                continue

            rb_id = f"rb:{rb['namespace']}:{rb['name']}"

            nodes.append(
                RBACGraph._node(
                    rb_id,
                    rb["name"],
                    "RoleBinding"
                )
            )

            edges.append(
                RBACGraph._edge(
                    rb_id,
                    role_id
                )
            )

            for subject in rb.get("subjects", []):

                if subject["kind"] == "ServiceAccount":

                    subject_id = (
                        f"ServiceAccount:"
                        f"{subject.get('namespace','default')}:"
                        f"{subject['name']}"
                    )

                else:

                    subject_id = (
                        f"{subject['kind']}:"
                        f"{subject['name']}"
                    )

                nodes.append(
                    RBACGraph._node(
                        subject_id,
                        subject["name"],
                        subject["kind"]
                    )
                )

                edges.append(
                    RBACGraph._edge(
                        subject_id,
                        rb_id
                    )
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
            RBACGraph._node(
                role_id,
                role["name"],
                "ClusterRole"
            )
        )
        for crb in bindings:

            if crb["role"] != role["name"]:
                continue

            crb_id = f"crb:{crb['name']}"

            nodes.append(
                RBACGraph._node(
                    crb_id,
                    crb["name"],
                    "ClusterRoleBinding"
                )
            )

            edges.append(
                RBACGraph._edge(
                    crb_id,
                    role_id
                )
            )

            for subject in crb.get("subjects", []):

                if subject["kind"] == "ServiceAccount":

                    subject_id = (
                        f"ServiceAccount:"
                        f"{subject.get('namespace','default')}:"
                        f"{subject['name']}"
                    )

                else:

                    subject_id = (
                        f"{subject['kind']}:"
                        f"{subject['name']}"
                    )

                nodes.append(
                    RBACGraph._node(
                        subject_id,
                        subject["name"],
                        subject["kind"]
                    )
                )

                edges.append(
                    RBACGraph._edge(
                        subject_id,
                        crb_id
                    )
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

        result = []

        seen = set()

        for item in items:

            key = tuple(sorted(item.items()))

            if key in seen:
                continue

            seen.add(key)

            result.append(item)

        return result