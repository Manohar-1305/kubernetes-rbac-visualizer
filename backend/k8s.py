from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


class KubernetesRBAC:

    def __init__(self):

        try:
            config.load_incluster_config()
        except ConfigException:
            config.load_kube_config()

        self.rbac = client.RbacAuthorizationV1Api()
        self.core = client.CoreV1Api()

    # -------------------------------------------------------
    # Helpers
    # -------------------------------------------------------

    def _normalize_rule(self, rule):

        return {
            "apiGroups": list(rule.api_groups or []),
            "resources": list(rule.resources or []),
            "verbs": list(rule.verbs or []),
            "resourceNames": list(rule.resource_names or []),
            "nonResourceURLs": list(rule.non_resource_urls or [])
        }

    def _get_role(self, namespace, name):

        try:

            role = self.rbac.read_namespaced_role(
                name=name,
                namespace=namespace
            )

            return {
                "kind": "Role",
                "name": role.metadata.name,
                "namespace": role.metadata.namespace,
                "rules": [
                    self._normalize_rule(rule)
                    for rule in (role.rules or [])
                ]
            }

        except Exception:

            return None

    def _get_cluster_role(self, name):

        try:

            role = self.rbac.read_cluster_role(
                name=name
            )

            return {
                "kind": "ClusterRole",
                "name": role.metadata.name,
                "rules": [
                    self._normalize_rule(rule)
                    for rule in (role.rules or [])
                ]
            }

        except Exception:

            return None

    def _resolve_role(self, namespace, role_name, role_kind):

        if role_kind == "Role":
            return self._get_role(namespace, role_name)

        return self._get_cluster_role(role_name)

    def _permission_summary(self, role):

        permissions = []

        if role is None:
            return permissions

        for rule in role["rules"]:

            permissions.append(
                {
                    "apiGroups": rule["apiGroups"],
                    "resources": rule["resources"],
                    "verbs": rule["verbs"],
                    "resourceNames": rule["resourceNames"],
                    "nonResourceURLs": rule["nonResourceURLs"]
                }
            )

        return permissions

    def _empty_identity(self, kind, name, namespace=None):

        return {
            "kind": kind,
            "name": name,
            "namespace": namespace,
            "roleBindings": [],
            "clusterRoleBindings": [],
            "permissions": []
        }

    def _add_permissions(self, identity, role):

        if role is None:
            return

        for rule in self._permission_summary(role):
            identity["permissions"].append(rule)

    # -------------------------------------------------------
    # Users
    # -------------------------------------------------------

    def get_users(self):

        users = {}

        role_bindings = self.rbac.list_role_binding_for_all_namespaces().items

        for rb in role_bindings:

            if not rb.subjects:
                continue

            role = self._resolve_role(
                rb.metadata.namespace,
                rb.role_ref.name,
                rb.role_ref.kind
            )

            for subject in rb.subjects:

                if subject.kind != "User":
                    continue

                if subject.name not in users:

                    users[subject.name] = self._empty_identity(
                        "User",
                        subject.name
                    )

                users[subject.name]["roleBindings"].append(
                    {
                        "name": rb.metadata.name,
                        "namespace": rb.metadata.namespace,
                        "role": rb.role_ref.name,
                        "kind": rb.role_ref.kind
                    }
                )

                self._add_permissions(
                    users[subject.name],
                    role
                )

        cluster_role_bindings = self.rbac.list_cluster_role_binding().items

        for crb in cluster_role_bindings:

            if not crb.subjects:
                continue

            role = self._get_cluster_role(
                crb.role_ref.name
            )

            for subject in crb.subjects:

                if subject.kind != "User":
                    continue

                if subject.name not in users:

                    users[subject.name] = self._empty_identity(
                        "User",
                        subject.name
                    )

                users[subject.name]["clusterRoleBindings"].append(
                    {
                        "name": crb.metadata.name,
                        "role": crb.role_ref.name,
                        "kind": crb.role_ref.kind
                    }
                )

                self._add_permissions(
                    users[subject.name],
                    role
                )

        return sorted(
            users.values(),
            key=lambda x: x["name"]
        )

    # -------------------------------------------------------
    # Groups
    # -------------------------------------------------------

    def get_groups(self):

        groups = {}

        role_bindings = self.rbac.list_role_binding_for_all_namespaces().items

        for rb in role_bindings:

            if not rb.subjects:
                continue

            role = self._resolve_role(
                rb.metadata.namespace,
                rb.role_ref.name,
                rb.role_ref.kind
            )

            for subject in rb.subjects:

                if subject.kind != "Group":
                    continue

                if subject.name not in groups:

                    groups[subject.name] = self._empty_identity(
                        "Group",
                        subject.name
                    )

                groups[subject.name]["roleBindings"].append(
                    {
                        "name": rb.metadata.name,
                        "namespace": rb.metadata.namespace,
                        "role": rb.role_ref.name,
                        "kind": rb.role_ref.kind
                    }
                )

                self._add_permissions(
                    groups[subject.name],
                    role
                )

        cluster_role_bindings = self.rbac.list_cluster_role_binding().items

        for crb in cluster_role_bindings:

            if not crb.subjects:
                continue

            role = self._get_cluster_role(
                crb.role_ref.name
            )

            for subject in crb.subjects:

                if subject.kind != "Group":
                    continue

                if subject.name not in groups:

                    groups[subject.name] = self._empty_identity(
                        "Group",
                        subject.name
                    )

                groups[subject.name]["clusterRoleBindings"].append(
                    {
                        "name": crb.metadata.name,
                        "role": crb.role_ref.name,
                        "kind": crb.role_ref.kind
                    }
                )

                self._add_permissions(
                    groups[subject.name],
                    role
                )

        return sorted(
            groups.values(),
            key=lambda x: x["name"]
        )

    # -------------------------------------------------------
    # Service Accounts
    # -------------------------------------------------------

    def get_service_accounts(self):

        service_accounts = {}

        accounts = self.core.list_service_account_for_all_namespaces().items

        for sa in accounts:

            key = f"{sa.metadata.namespace}:{sa.metadata.name}"

            service_accounts[key] = self._empty_identity(
                "ServiceAccount",
                sa.metadata.name,
                sa.metadata.namespace
            )
            role_bindings = self.rbac.list_role_binding_for_all_namespaces().items

        for rb in role_bindings:

            if not rb.subjects:
                continue

            role = self._resolve_role(
                rb.metadata.namespace,
                rb.role_ref.name,
                rb.role_ref.kind
            )

            for subject in rb.subjects:

                if subject.kind != "ServiceAccount":
                    continue

                namespace = getattr(
                    subject,
                    "namespace",
                    rb.metadata.namespace
                )

                key = f"{namespace}:{subject.name}"

                if key not in service_accounts:
                    continue

                service_accounts[key]["roleBindings"].append(
                    {
                        "name": rb.metadata.name,
                        "namespace": rb.metadata.namespace,
                        "role": rb.role_ref.name,
                        "kind": rb.role_ref.kind
                    }
                )

                self._add_permissions(
                    service_accounts[key],
                    role
                )

        cluster_role_bindings = self.rbac.list_cluster_role_binding().items

        for crb in cluster_role_bindings:

            if not crb.subjects:
                continue

            role = self._get_cluster_role(
                crb.role_ref.name
            )

            for subject in crb.subjects:

                if subject.kind != "ServiceAccount":
                    continue

                namespace = getattr(
                    subject,
                    "namespace",
                    None
                )

                if namespace is None:
                    continue

                key = f"{namespace}:{subject.name}"

                if key not in service_accounts:
                    continue

                service_accounts[key]["clusterRoleBindings"].append(
                    {
                        "name": crb.metadata.name,
                        "role": crb.role_ref.name,
                        "kind": crb.role_ref.kind
                    }
                )

                self._add_permissions(
                    service_accounts[key],
                    role
                )

        return sorted(
            service_accounts.values(),
            key=lambda x: (
                x["namespace"],
                x["name"]
            )
        )

    # -------------------------------------------------------
    # Roles
    # -------------------------------------------------------

    def get_roles(self):

        result = []

        roles = self.rbac.list_role_for_all_namespaces().items

        for role in roles:

            result.append(
                {
                    "kind": "Role",
                    "name": role.metadata.name,
                    "namespace": role.metadata.namespace,
                    "rules": [
                        self._normalize_rule(rule)
                        for rule in (role.rules or [])
                    ]
                }
            )

        return sorted(
            result,
            key=lambda x: (
                x["namespace"],
                x["name"]
            )
        )

    # -------------------------------------------------------
    # Cluster Roles
    # -------------------------------------------------------

    def get_cluster_roles(self):

        result = []

        roles = self.rbac.list_cluster_role().items

        for role in roles:

            result.append(
                {
                    "kind": "ClusterRole",
                    "name": role.metadata.name,
                    "rules": [
                        self._normalize_rule(rule)
                        for rule in (role.rules or [])
                    ]
                }
            )

        return sorted(
            result,
            key=lambda x: x["name"]
        )
    # -------------------------------------------------------
    # Role Bindings
    # -------------------------------------------------------

    def get_role_bindings(self):

        result = []

        bindings = self.rbac.list_role_binding_for_all_namespaces().items

        for rb in bindings:

            subjects = []

            if rb.subjects:

                for subject in rb.subjects:

                    subjects.append(
                        {
                            "kind": subject.kind,
                            "name": subject.name,
                            "namespace": getattr(
                                subject,
                                "namespace",
                                None
                            )
                        }
                    )

            role = self._resolve_role(
                rb.metadata.namespace,
                rb.role_ref.name,
                rb.role_ref.kind
            )

            result.append(
                {
                    "name": rb.metadata.name,
                    "namespace": rb.metadata.namespace,
                    "role": rb.role_ref.name,
                    "kind": rb.role_ref.kind,
                    "subjects": subjects,
                    "permissions": self._permission_summary(role)
                }
            )

        return sorted(
            result,
            key=lambda x: (
                x["namespace"],
                x["name"]
            )
        )

    # -------------------------------------------------------
    # Cluster Role Bindings
    # -------------------------------------------------------

    def get_cluster_role_bindings(self):

        result = []

        bindings = self.rbac.list_cluster_role_binding().items

        for crb in bindings:

            subjects = []

            if crb.subjects:

                for subject in crb.subjects:

                    subjects.append(
                        {
                            "kind": subject.kind,
                            "name": subject.name,
                            "namespace": getattr(
                                subject,
                                "namespace",
                                None
                            )
                        }
                    )

            role = self._get_cluster_role(
                crb.role_ref.name
            )

            result.append(
                {
                    "name": crb.metadata.name,
                    "role": crb.role_ref.name,
                    "kind": crb.role_ref.kind,
                    "subjects": subjects,
                    "permissions": self._permission_summary(role)
                }
            )

        return sorted(
            result,
            key=lambda x: x["name"]
        )

    # -------------------------------------------------------
    # Lookup Methods
    # -------------------------------------------------------

    def get_user(self, name):

        for user in self.get_users():

            if user["name"] == name:
                return user

        return None

    def get_group(self, name):

        for group in self.get_groups():

            if group["name"] == name:
                return group

        return None

    def get_service_account(self, namespace, name):

        for sa in self.get_service_accounts():

            if sa["namespace"] == namespace and sa["name"] == name:
                return sa

        return None

    def get_role(self, namespace, name):

        for role in self.get_roles():

            if role["namespace"] == namespace and role["name"] == name:
                return role

        return None

    def get_cluster_role_details(self, name):

        for role in self.get_cluster_roles():

            if role["name"] == name:
                return role

        return None