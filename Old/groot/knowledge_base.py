# groot/knowledge_base.py
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class KnowledgeBase:
    """Knowledge base for common Kubernetes and cloud issues and solutions."""

    def __init__(self, kb_dir: str = None):
        """Initialize the knowledge base."""
        self.kb_dir = kb_dir or os.path.expanduser("~/.groot/knowledge_base")
        self.ensure_kb_exists()
        self.kb_cache = {}
        self.load_kb()

    def ensure_kb_exists(self):
        """Ensure knowledge base directory exists and has default data."""
        kb_path = Path(self.kb_dir)
        kb_path.mkdir(parents=True, exist_ok=True)

        # Create default knowledge base files if they don't exist
        self._create_default_kb_file("pod_issues.json", self._default_pod_issues())
        self._create_default_kb_file("deployment_issues.json", self._default_deployment_issues())
        self._create_default_kb_file("networking_issues.json", self._default_networking_issues())
        self._create_default_kb_file("storage_issues.json", self._default_storage_issues())
        self._create_default_kb_file("security_issues.json", self._default_security_issues())
        self._create_default_kb_file("aws_issues.json", self._default_aws_issues())
        self._create_default_kb_file("gcp_issues.json", self._default_gcp_issues())
        self._create_default_kb_file("azure_issues.json", self._default_azure_issues())
        self._create_default_kb_file("best_practices.json", self._default_best_practices())

    def _create_default_kb_file(self, filename: str, default_data: Dict):
        """Create a default knowledge base file if it doesn't exist."""
        file_path = Path(self.kb_dir) / filename
        if not file_path.exists():
            with open(file_path, 'w') as f:
                json.dump(default_data, f, indent=2)

    def load_kb(self):
        """Load all knowledge base files into memory."""
        kb_path = Path(self.kb_dir)
        for file_path in kb_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    self.kb_cache[file_path.stem] = json.load(f)
            except Exception as e:
                print(f"Error loading knowledge base file {file_path}: {e}")

    def search(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search the knowledge base for relevant entries based on the query."""
        results = []

        # Extract search parameters
        resource_types = query.get("entities", {}).get("resource_type", [])
        issue_types = query.get("entities", {}).get("issue_type", [])
        cloud_providers = query.get("entities", {}).get("cloud_provider", [])

        # Search in pod issues
        if not resource_types or "pod" in resource_types:
            pod_results = self._search_category("pod_issues", issue_types)
            results.extend(pod_results)

        # Search in deployment issues
        if not resource_types or "deployment" in resource_types:
            deployment_results = self._search_category("deployment_issues", issue_types)
            results.extend(deployment_results)

        # Search in networking issues
        if not issue_types or "network" in issue_types:
            network_results = self._search_category("networking_issues", issue_types)
            results.extend(network_results)

        # Search in storage issues
        if not issue_types or "storage" in issue_types:
            storage_results = self._search_category("storage_issues", issue_types)
            results.extend(storage_results)

        # Search in security issues
        if not issue_types or "security" in issue_types:
            security_results = self._search_category("security_issues", issue_types)
            results.extend(security_results)

        # Search in cloud provider issues
        if cloud_providers:
            for provider in cloud_providers:
                provider_results = self._search_category(f"{provider}_issues", issue_types)
                results.extend(provider_results)

        # Add best practices if few results
        if len(results) < 3:
            best_practices = self._search_category("best_practices", resource_types)
            results.extend(best_practices[:2])  # Add up to 2 best practices

        # Sort by relevance (currently just prioritizing exact matches)
        if resource_types and issue_types:
            results.sort(key=lambda x: (
                # Prioritize entries that match both resource and issue type
                any(rt in x.get("resource_types", []) for rt in resource_types) and
                any(it in x.get("issue_types", []) for it in issue_types),
                # Then prioritize entries that match resource type
                any(rt in x.get("resource_types", []) for rt in resource_types),
                # Then prioritize entries that match issue type
                any(it in x.get("issue_types", []) for it in issue_types)
            ), reverse=True)

        # Limit to top 5 results
        return results[:5]

    def _search_category(self, category: str, filters: List[str]) -> List[Dict[str, Any]]:
        """Search a specific category of the knowledge base."""
        if category not in self.kb_cache:
            return []

        entries = self.kb_cache[category].get("entries", [])

        # If no filters, return all entries
        if not filters:
            return entries

        # Filter entries by the provided filters
        results = []
        for entry in entries:
            # Check if any filter matches any tag in the entry
            if any(f in entry.get("tags", []) for f in filters):
                results.append(entry)

        return results

    def add_entry(self, category: str, entry: Dict[str, Any]) -> bool:
        """Add a new entry to the knowledge base."""
        if category not in self.kb_cache:
            self.kb_cache[category] = {"entries": []}

        # Add the entry
        self.kb_cache[category]["entries"].append(entry)

        # Save to disk
        try:
            file_path = Path(self.kb_dir) / f"{category}.json"
            with open(file_path, 'w') as f:
                json.dump(self.kb_cache[category], f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving knowledge base entry: {e}")
            return False

    def _default_pod_issues(self) -> Dict:
        """Default knowledge base for pod issues."""
        return {
            "entries": [
                {
                    "title": "CrashLoopBackOff",
                    "description": "Pod is crashing and Kubernetes is repeatedly trying to restart it",
                    "resource_types": ["pod"],
                    "issue_types": ["crash"],
                    "tags": ["crash", "pod", "container", "restart"],
                    "symptoms": [
                        "Pod status shows 'CrashLoopBackOff'",
                        "Pod is repeatedly restarting",
                        "Container exit code is non-zero"
                    ],
                    "causes": [
                        "Application error causing the container to exit",
                        "Misconfiguration in the container command or arguments",
                        "Resource constraints (OOM)",
                        "Liveness probe failure"
                    ],
                    "solutions": [
                        "Check container logs: `kubectl logs <pod-name> -n <namespace>`",
                        "Check events: `kubectl describe pod <pod-name> -n <namespace>`",
                        "Verify container command and arguments",
                        "Check resource limits and increase if necessary",
                        "Verify liveness probe configuration"
                    ],
                    "commands": [
                        "kubectl logs <pod-name> -n <namespace>",
                        "kubectl describe pod <pod-name> -n <namespace>",
                        "kubectl get events -n <namespace> --sort-by='.lastTimestamp'"
                    ],
                    "references": [
                        "https://kubernetes.io/docs/tasks/debug-application-cluster/debug-application/#debugging-pods"
                    ]
                },
                {
                    "title": "ImagePullBackOff",
                    "description": "Kubernetes cannot pull the container image",
                    "resource_types": ["pod"],
                    "issue_types": ["configuration"],
                    "tags": ["image", "pod", "container", "registry"],
                    "symptoms": [
                        "Pod status shows 'ImagePullBackOff' or 'ErrImagePull'",
                        "Pod cannot start",
                        "Events show image pull errors"
                    ],
                    "causes": [
                        "Image does not exist in the registry",
                        "Image tag is incorrect",
                        "Registry requires authentication",
                        "Network issues preventing access to the registry"
                    ],
                    "solutions": [
                        "Verify image name and tag",
                        "Check if the image exists in the registry",
                        "Ensure registry credentials are correct",
                        "Create or update image pull secrets",
                        "Check network connectivity to the registry"
                    ],
                    "commands": [
                        "kubectl describe pod <pod-name> -n <namespace>",
                        "kubectl create secret docker-registry <secret-name> --docker-server=<registry> --docker-username=<username> --docker-password=<password>",
                        "kubectl patch serviceaccount <sa-name> -p '{\"imagePullSecrets\": [{\"name\": \"<secret-name>\"}]}'"
                    ],
                    "references": [
                        "https://kubernetes.io/docs/concepts/containers/images/#using-a-private-registry"
                    ]
                },
                # More pod issues...
            ]
        }

    def _default_deployment_issues(self) -> Dict:
        """Default knowledge base for deployment issues."""
        return {
            "entries": [
                {
                    "title": "Deployment Rollout Stuck",
                    "description": "Deployment rollout is stuck and not progressing",
                    "resource_types": ["deployment"],
                    "issue_types": ["configuration"],
                    "tags": ["deployment", "rollout", "stuck", "update"],
                    "symptoms": [
                        "Deployment shows 'progressing' but never completes",
                        "New pods are not being created or are stuck in pending",
                        "Old pods are not being terminated"
                    ],
                    "causes": [
                        "Insufficient cluster resources",
                        "Pod scheduling issues",
                        "Readiness probe failures",
                        "Image pull issues",
                        "PVC binding issues"
                    ],
                    "solutions": [
                        "Check deployment status: `kubectl rollout status deployment/<name>`",
                        "Check pod events: `kubectl get events -n <namespace>`",
                        "Check readiness probe configuration",
                        "Verify resource requests and limits",
                        "Check PVC status if applicable"
                    ],
                    "commands": [
                        "kubectl rollout status deployment/<name> -n <namespace>",
                        "kubectl get events -n <namespace> --sort-by='.lastTimestamp'",
                        "kubectl describe deployment <name> -n <namespace>",
                        "kubectl rollout undo deployment/<name> -n <namespace>"
                    ],
                    "references": [
                        "https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#deployment-status"
                    ]
                },
                # More deployment issues...
            ]
        }

    def _default_networking_issues(self) -> Dict:
        """Default knowledge base for networking issues."""
        return {
            "entries": [
                {
                    "title": "Service Not Accessible",
                    "description": "Kubernetes service is not accessible from other pods or externally",
                    "resource_types": ["service"],
                    "issue_types": ["network"],
                    "tags": ["service", "network", "connectivity", "dns"],
                    "symptoms": [
                        "Cannot connect to service from other pods",
                        "External access to service fails",
                        "DNS resolution for service fails"
                    ],
                    "causes": [
                        "Service selector doesn't match pod labels",
                        "Pods are not running or not ready",
                        "Network policy blocking traffic",
                        "Service ports don't match container ports",
                        "kube-proxy issues",
                        "CNI plugin issues"
                    ],
                    "solutions": [
                        "Verify service selector matches pod labels",
                        "Check if pods are running and ready",
                        "Verify network policies",
                        "Check service and pod port configurations",
                        "Test connectivity with temporary debug pod"
                    ],
                    "commands": [
                        "kubectl get svc <service-name> -n <namespace> -o yaml",
                        "kubectl get pods -l <selector> -n <namespace>",
                        "kubectl get networkpolicies -n <namespace>",
                        "kubectl run tmp-shell --rm -i --tty --image nicolaka/netshoot -- /bin/bash",
                        "kubectl exec -it <pod-name> -n <namespace> -- nslookup <service-name>"
                    ],
                    "references": [
                        "https://kubernetes.io/docs/concepts/services-networking/service/#debugging-services"
                    ]
                },
                # More networking issues...
            ]
        }

    def _default_storage_issues(self) -> Dict:
        """Default knowledge base for storage issues."""
        return {
            "entries": [
                {
                    "title": "PVC Stuck in Pending",
                    "description": "Persistent Volume Claim is stuck in pending state",
                    "resource_types": ["pvc", "pv"],
                    "issue_types": ["storage"],
                    "tags": ["pvc", "storage", "volume", "pending"],
                    "symptoms": [
                        "PVC status shows 'Pending'",
                        "Pod using the PVC is stuck in 'ContainerCreating'",
                        "Events show volume provisioning issues"
                    ],
                    "causes": [
                        "No storage class defined",
                        "Storage class provisioner is not running",
                        "Storage backend issues",
                        "Insufficient capacity in storage backend",
                        "Access mode conflicts"
                    ],
                    "solutions": [
                        "Check PVC status and events",
                        "Verify storage class exists and is default if not specified",
                        "Check storage provisioner pods",
                        "Verify access modes are compatible",
                        "Check storage backend capacity and health"
                    ],
                    "commands": [
                        "kubectl get pvc -n <namespace>",
                        "kubectl describe pvc <pvc-name> -n <namespace>",
                        "kubectl get sc",
                        "kubectl get pods -n kube-system | grep provisioner"
                    ],
                    "references": [
                        "https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims"
                    ]
                },
                # More storage issues...
            ]
        }

    def _default_security_issues(self) -> Dict:
        """Default knowledge base for security issues."""
        return {
            "entries": [
                {
                    "title": "RBAC Permission Denied",
                    "description": "Kubernetes API requests are being denied due to RBAC permissions",
                    "resource_types": ["pod", "deployment", "serviceaccount"],
                    "issue_types": ["security"],
                    "tags": ["rbac", "permissions", "access", "forbidden", "serviceaccount"],
                    "symptoms": [
                        "Error messages containing 'forbidden' or 'unauthorized'",
                        "Service accounts cannot access required resources",
                        "Pods cannot access the Kubernetes API"
                    ],
                    "causes": [
                        "Missing Role or ClusterRole",
                        "Missing RoleBinding or ClusterRoleBinding",
                        "ServiceAccount not properly configured",
                        "Pod not using the correct ServiceAccount"
                    ],
                    "solutions": [
                        "Check the ServiceAccount used by the pod",
                        "Verify Roles and RoleBindings",
                        "Create appropriate RBAC resources",
                        "Use 'kubectl auth can-i' to test permissions"
                    ],
                    "commands": [
                        "kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.serviceAccountName}'",
                        "kubectl get roles -n <namespace>",
                        "kubectl get rolebindings -n <namespace>",
                        "kubectl auth can-i <verb> <resource> --as=system:serviceaccount:<namespace>:<serviceaccount>",
                        "kubectl create role <role-name> --verb=<verbs> --resource=<resources> -n <namespace>",
                        "kubectl create rolebinding <binding-name> --role=<role-name> --serviceaccount=<namespace>:<serviceaccount> -n <namespace>"
                    ],
                    "references": [
                        "https://kubernetes.io/docs/reference/access-authn-authz/rbac/"
                    ]
                },
                # More security issues...
            ]
        }

    def _default_aws_issues(self) -> Dict:
        """Default knowledge base for AWS issues."""
        return {
            "entries": [
                {
                    "title": "EKS Node Group Scaling Issues",
                    "description": "EKS node group is not scaling properly",
                    "resource_types": ["node"],
                    "issue_types": ["scaling"],
                    "tags": ["aws", "eks", "node", "scaling", "autoscaling"],
                    "symptoms": [
                        "Pods remain in pending state despite high resource utilization",
                        "Node group is not scaling up or down as expected",
                        "Cluster Autoscaler logs show errors"
                    ],
                    "causes": [
                        "IAM permissions issues for Cluster Autoscaler",
                        "ASG min/max settings are too restrictive",
                        "Resource requests not set properly",
                        "Cluster Autoscaler configuration issues",
                        "AWS service quotas reached"
                    ],
                    "solutions": [
                        "Verify IAM permissions for Cluster Autoscaler",
                        "Check ASG min/max settings",
                        "Ensure pods have appropriate resource requests",
                        "Check Cluster Autoscaler logs",
                        "Verify AWS service quotas"
                    ],
                    "commands": [
                        "kubectl logs -n kube-system -l app=cluster-autoscaler",
                        "aws eks describe-nodegroup --cluster-name <cluster-name> --nodegroup-name <nodegroup-name>",
                        "aws autoscaling describe-auto-scaling-groups --auto-scaling-group-names <asg-name>",
                        "kubectl get pods -A -o wide | grep Pending"
                    ],
                    "references": [
                        "https://docs.aws.amazon.com/eks/latest/userguide/cluster-autoscaler.html"
                    ]
                },
                # More AWS issues...
            ]
        }

    def _default_gcp_issues(self) -> Dict:
        """Default knowledge base for GCP issues."""
        return {
            "entries": [
                {
                    "title": "GKE Node Pool Issues",
                    "description": "GKE node pool is experiencing issues",
                    "resource_types": ["node"],
                    "issue_types": ["scaling", "performance"],
                    "tags": ["gcp", "gke", "node", "scaling", "autoscaling"],
                    "symptoms": [
                        "Nodes showing 'NotReady' status",
                        "Node pool not scaling as expected",
                        "High resource utilization on nodes"
                    ],
                    "causes": [
                        "Insufficient quota in GCP project",
                        "Autoscaling configuration issues",
                        "Node image issues",
                        "Network connectivity problems"
                    ],
                    "solutions": [
                        "Check node status and events",
                        "Verify GCP quotas",
                        "Check autoscaling configuration",
                        "Verify network connectivity",
                        "Check node logs in Cloud Logging"
                    ],
                    "commands": [
                        "kubectl get nodes",
                        "kubectl describe node <node-name>",
                        "gcloud container clusters describe <cluster-name> --zone <zone>",
                        "gcloud container node-pools describe <pool-name> --cluster <cluster-name> --zone <zone>"
                    ],
                    "references": [
                        "https://cloud.google.com/kubernetes-engine/docs/how-to/node-auto-scaling"
                    ]
                },
                # More GCP issues...
            ]
        }

    def _default_azure_issues(self) -> Dict:
        """Default knowledge base for Azure issues."""
        return {
            "entries": [
                {
                    "title": "AKS Node Issues",
                    "description": "AKS nodes are experiencing problems",
                    "resource_types": ["node"],
                    "issue_types": ["performance", "scaling"],
                    "tags": ["azure", "aks", "node", "scaling"],
                    "symptoms": [
                        "Nodes showing 'NotReady' status",
                        "Node pool not scaling as expected",
                        "Pods stuck in pending state"
                    ],
                    "causes": [
                        "Azure subscription quota limits",
                        "VMSS issues",
                        "Network security group blocking required traffic",
                        "Azure CNI IP address exhaustion"
                    ],
                    "solutions": [
                        "Check node status and events",
                        "Verify Azure quotas",
                        "Check VMSS status",
                        "Verify network security groups",
                        "Check for IP address exhaustion with Azure CNI"
                    ],
                    "commands": [
                        "kubectl get nodes",
                        "kubectl describe node <node-name>",
                        "az aks show -g <resource-group> -n <cluster-name>",
                        "az aks nodepool list -g <resource-group> --cluster-name <cluster-name>"
                    ],
                    "references": [
                        "https://docs.microsoft.com/en-us/azure/aks/troubleshooting"
                    ]
                },
                # More Azure issues...
            ]
        }

    def _default_best_practices(self) -> Dict:
        """Default knowledge base for Kubernetes best practices."""
        return {
            "entries": [
                {
                    "title": "Resource Requests and Limits",
                    "description": "Best practices for setting resource requests and limits",
                    "resource_types": ["pod", "deployment", "statefulset", "daemonset"],
                    "tags": ["best-practice", "resources", "performance", "stability"],
                    "content": "Always set resource requests and limits for containers to ensure proper scheduling and prevent resource contention. Start with monitoring actual usage and then set requests at P90 and limits higher based on application behavior. For critical applications, set CPU requests equal to limits to prevent CPU throttling, but keep memory limits higher than requests to account for spikes.",
                    "examples": [
                        {
                            "title": "Example resource configuration",
                            "yaml": """
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
"""
                        }
                    ],
                    "references": [
                        "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/"
                    ]
                },
                {
                    "title": "Pod Disruption Budgets",
                    "description": "Using PDBs to ensure application availability during disruptions",
                    "resource_types": ["deployment", "statefulset"],
                    "tags": ["best-practice", "availability", "disruption", "maintenance"],
                    "content": "Use Pod Disruption Budgets (PDBs) to ensure that a minimum number of pods remain available during voluntary disruptions like node drains or cluster upgrades. This is especially important for stateful applications and critical services.",
                    "examples": [
                        {
                            "title": "Example PDB configuration",
                            "yaml": """
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2  # or use maxUnavailable
  selector:
    matchLabels:
      app: my-app
"""
                        }
                    ],
                    "references": [
                        "https://kubernetes.io/docs/tasks/run-application/configure-pdb/"
                    ]
                },
                # More best practices...
            ]
        }