from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException


class KubernetesRBAC:

    def __init__(self):
        self._load_config()

        self.rbac = client.RbacAuthorizationV1Api()
        self.core = client.CoreV1Api()

    def _load_config(self):
        """
        Load Kubernetes configuration.

        Priority:
        1. In-cluster configuration
        2. Local kubeconfig (for development)
        """
        try:
            config.load_incluster_config()
            print("Loaded in-cluster Kubernetes configuration.")
        except ConfigException:
            config.load_kube_config()
            print("Loaded local kubeconfig.")

    # ------------------------------------------------------------------
    # Roles
    # ------------------------------------------------------------------

    def get_roles(self):
        return self.rbac.list_role_for_all_namespaces().items

    # ------------------------------------------------------------------
    # ClusterRoles
    # ------------------------------------------------------------------

    def get_cluster_roles(self):
        return self.rbac.list_cluster_role().items

    # ------------------------------------------------------------------
    # RoleBindings
    # ------------------------------------------------------------------

    def get_role_bindings(self):
        return self.rbac.list_role_binding_for_all_namespaces().items

    # ------------------------------------------------------------------
    # ClusterRoleBindings
    # ------------------------------------------------------------------

    def get_cluster_role_bindings(self):
        return self.rbac.list_cluster_role_binding().items

    # ------------------------------------------------------------------
    # Service Accounts
    # ------------------------------------------------------------------

    def get_service_accounts(self):
        return self.core.list_service_account_for_all_namespaces().items

    # ------------------------------------------------------------------
    # Users / Groups / ServiceAccounts from Bindings
    # ------------------------------------------------------------------

    def get_subjects(self):

        subjects = []

        for rb in self.get_role_bindings():
            if rb.subjects:
                for subject in rb.subjects:
                    subjects.append(
                        {
                            "kind": subject.kind,
                            "name": subject.name,
                            "namespace": getattr(subject, "namespace", None),
                        }
                    )

        for crb in self.get_cluster_role_bindings():
            if crb.subjects:
                for subject in crb.subjects:
                    subjects.append(
                        {
                            "kind": subject.kind,
                            "name": subject.name,
                            "namespace": getattr(subject, "namespace", None),
                        }
                    )

        return subjects

    # ------------------------------------------------------------------
    # Complete RBAC Data
    # ------------------------------------------------------------------

    def get_rbac_data(self):

        return {
            "roles": self.get_roles(),
            "cluster_roles": self.get_cluster_roles(),
            "role_bindings": self.get_role_bindings(),
            "cluster_role_bindings": self.get_cluster_role_bindings(),
            "service_accounts": self.get_service_accounts(),
            "subjects": self.get_subjects(),
        }