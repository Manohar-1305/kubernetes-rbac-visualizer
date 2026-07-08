from models import GraphNode, GraphEdge, GraphResponse


class RBACGraphBuilder:

    def __init__(self, data):
        self.data = data
        self.nodes = {}
        self.edges = []

    # -------------------------------------------------------------
    # Public
    # -------------------------------------------------------------

    def build(self) -> GraphResponse:

        self._add_roles()
        self._add_cluster_roles()
        self._add_role_bindings()
        self._add_cluster_role_bindings()
        self._connect_role_bindings()
        self._connect_cluster_role_bindings()

        return GraphResponse(
            nodes=list(self.nodes.values()),
            edges=self.edges,
        )

    # -------------------------------------------------------------
    # Node Helpers
    # -------------------------------------------------------------

    def _node_id(self, kind, namespace, name):

        namespace = namespace or "cluster"
        return f"{kind}:{namespace}:{name}"

    def _add_node(self, kind, name, namespace=None):

        node_id = self._node_id(kind, namespace, name)

        if node_id not in self.nodes:
            self.nodes[node_id] = GraphNode(
                id=node_id,
                label=name,
                kind=kind,
                namespace=namespace,
            )

        return node_id

    def _add_edge(self, source, target, relation):

        self.edges.append(
            GraphEdge(
                source=source,
                target=target,
                relation=relation,
            )
        )

    # -------------------------------------------------------------
    # Roles
    # -------------------------------------------------------------

    def _add_roles(self):

        for role in self.data["roles"]:
            self._add_node(
                kind="Role",
                name=role.metadata.name,
                namespace=role.metadata.namespace,
            )

    # -------------------------------------------------------------
    # ClusterRoles
    # -------------------------------------------------------------

    def _add_cluster_roles(self):

        for role in self.data["cluster_roles"]:
            self._add_node(
                kind="ClusterRole",
                name=role.metadata.name,
            )

    # -------------------------------------------------------------
    # RoleBindings
    # -------------------------------------------------------------

    def _add_role_bindings(self):

        for rb in self.data["role_bindings"]:
            rb_node = self._add_node(
                kind="RoleBinding",
                name=rb.metadata.name,
                namespace=rb.metadata.namespace,
            )

            if rb.subjects:
                for subject in rb.subjects:

                    subject_node = self._add_node(
                        kind=subject.kind,
                        name=subject.name,
                        namespace=getattr(subject, "namespace", None),
                    )

                    self._add_edge(
                        source=subject_node,
                        target=rb_node,
                        relation="BOUND_TO",
                    )

    # -------------------------------------------------------------
    # ClusterRoleBindings
    # -------------------------------------------------------------

    def _add_cluster_role_bindings(self):

        for crb in self.data["cluster_role_bindings"]:

            crb_node = self._add_node(
                kind="ClusterRoleBinding",
                name=crb.metadata.name,
            )

            if crb.subjects:
                for subject in crb.subjects:

                    subject_node = self._add_node(
                        kind=subject.kind,
                        name=subject.name,
                        namespace=getattr(subject, "namespace", None),
                    )

                    self._add_edge(
                        source=subject_node,
                        target=crb_node,
                        relation="BOUND_TO",
                    )

    # -------------------------------------------------------------
    # Connect RoleBinding -> Role
    # -------------------------------------------------------------

    def _connect_role_bindings(self):

        for rb in self.data["role_bindings"]:

            rb_node = self._node_id(
                "RoleBinding",
                rb.metadata.namespace,
                rb.metadata.name,
            )

            ref = rb.role_ref

            target = self._node_id(
                ref.kind,
                rb.metadata.namespace if ref.kind == "Role" else None,
                ref.name,
            )

            self._add_edge(
                source=rb_node,
                target=target,
                relation="GRANTS",
            )

    # -------------------------------------------------------------
    # Connect ClusterRoleBinding -> ClusterRole
    # -------------------------------------------------------------

    def _connect_cluster_role_bindings(self):

        for crb in self.data["cluster_role_bindings"]:

            crb_node = self._node_id(
                "ClusterRoleBinding",
                None,
                crb.metadata.name,
            )

            ref = crb.role_ref

            target = self._node_id(
                ref.kind,
                None,
                ref.name,
            )

            self._add_edge(
                source=crb_node,
                target=target,
                relation="GRANTS",
            )