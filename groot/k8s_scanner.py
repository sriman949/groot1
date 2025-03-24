"""
Kubernetes scanner module for Groot
"""

import asyncio
from typing import List, Dict, Any, Tuple, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from rich.console import Console

console = Console()

class K8sScanner:
    """Enhanced Kubernetes scanner with comprehensive resource analysis."""

    def __init__(self):
        try:
            config.load_kube_config()
        except Exception:
            try:
                config.load_incluster_config()
            except Exception:
                console.print("[bold red]Error: Could not configure Kubernetes client. Check your kubeconfig.[/bold red]")
                return

        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.custom_api = client.CustomObjectsApi()
        self.api_client = client.ApiClient()

    async def get_namespaces(self) -> List[str]:
        """Get all namespaces in the cluster."""
        try:
            namespaces = self.core_v1.list_namespace()
            return [ns.metadata.name for ns in namespaces.items]
        except ApiException as e:
            console.print(f"[red]Error getting namespaces: {e}[/red]")
            return []

    async def get_pods(self, namespace: str = None) -> List[Any]:
        """Get all pods, optionally filtered by namespace."""
        try:
            if namespace:
                pods = self.core_v1.list_namespaced_pod(namespace)
            else:
                pods = self.core_v1.list_pod_for_all_namespaces()
            return pods.items
        except ApiException as e:
            console.print(f"[red]Error getting pods: {e}[/red]")
            return []

    async def get_deployments(self, namespace: str = None) -> List[Tuple[str, int, str]]:
        """Get all deployments with their status."""
        try:
            if namespace:
                deployments = self.apps_v1.list_namespaced_deployment(namespace)
            else:
                deployments = self.apps_v1.list_deployment_for_all_namespaces()

            result = []
            for d in deployments.items:
                name = d.metadata.name
                replicas = d.spec.replicas
                available = d.status.available_replicas or 0
                status = "Healthy" if available == replicas else f"Unhealthy ({available}/{replicas})"
                result.append((name, replicas, status))
            return result
        except ApiException as e:
            console.print(f"[red]Error getting deployments: {e}[/red]")
            return []

    async def get_services(self, namespace: str = None) -> List[Tuple[str, str]]:
        """Get all services with their type."""
        try:
            if namespace:
                services = self.core_v1.list_namespaced_service(namespace)
            else:
                services = self.core_v1.list_service_for_all_namespaces()

            return [(s.metadata.name, s.spec.type) for s in services.items]
        except ApiException as e:
            console.print(f"[red]Error getting services: {e}[/red]")
            return []

    async def get_custom_resources(self, group: str, version: str, plural: str, namespace: str = None) -> List[Dict]:
        """Get custom resources of a specific type."""
        try:
            if namespace:
                resources = self.custom_api.list_namespaced_custom_object(
                    group, version, namespace, plural
                )
            else:
                resources = self.custom_api.list_cluster_custom_object(
                    group, version, plural
                )
            return resources.get('items', [])
        except ApiException as e:
            console.print(f"[red]Error getting custom resources: {e}[/red]")
            return []

    async def get_pod_logs(self, pod_name: str, namespace: str, tail_lines: int = 50) -> str:
        """Get logs for a specific pod."""
        try:
            return self.core_v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=tail_lines
            )
        except ApiException as e:
            return f"Error getting logs: {e}"

    async def describe_resource(self, resource_type: str, name: str, namespace: str = None) -> Dict:
        """Get detailed information about a specific resource."""
        try:
            if resource_type == "pod":
                if namespace:
                    return self.core_v1.read_namespaced_pod(name, namespace).to_dict()
                else:
                    # Find the pod in all namespaces
                    pods = self.core_v1.list_pod_for_all_namespaces()
                    for pod in pods.items:
                        if pod.metadata.name == name:
                            return pod.to_dict()
            elif resource_type == "deployment":
                if namespace:
                    return self.apps_v1.read_namespaced_deployment(name, namespace).to_dict()
                else:
                    deployments = self.apps_v1.list_deployment_for_all_namespaces()
                    for dep in deployments.items:
                        if dep.metadata.name == name:
                            return dep.to_dict()
            elif resource_type == "service":
                if namespace:
                    return self.core_v1.read_namespaced_service(name, namespace).to_dict()
                else:
                    services = self.core_v1.list_service_for_all_namespaces()
                    for svc in services.items:
                        if svc.metadata.name == name:
                            return svc.to_dict()
            # Add more resource types as needed

            return {"error": f"Resource {resource_type}/{name} not found"}
        except ApiException as e:
            return {"error": f"Error describing resource: {e}"}

    async def get_events(self, namespace: str = None, field_selector: str = None) -> List[Dict]:
        """Get events, optionally filtered by namespace and field selector."""
        try:
            if namespace:
                events = self.core_v1.list_namespaced_event(
                    namespace,
                    field_selector=field_selector
                )
            else:
                events = self.core_v1.list_event_for_all_namespaces(
                    field_selector=field_selector
                )

            return [event.to_dict() for event in events.items]
        except ApiException as e:
            console.print(f"[red]Error getting events: {e}[/red]")
            return []

    async def analyze_resources(self, namespace: str = None) -> List[Dict]:
        """Analyze Kubernetes resources for issues."""
        issues = []

        # Get resources
        pods = await self.get_pods(namespace)
        deployments = await self.get_deployments(namespace)

        # Check for pod issues
        for pod in pods:
            pod_name = pod.metadata.name
            pod_namespace = pod.metadata.namespace

            # Skip if not in the requested namespace
            if namespace and pod_namespace != namespace:
                continue

            # Check pod status
            if pod.status.phase != 'Running':
                issue = {
                    "resource_type": "pod",
                    "name": pod_name,
                    "namespace": pod_namespace,
                    "severity": "high" if pod.status.phase == 'Failed' else "medium",
                    "issue": f"Pod {pod_name} is in {pod.status.phase} state",
                    "context": {}
                }

                # Get pod events for context
                field_selector = f"involvedObject.name={pod_name}"
                events = await self.get_events(pod_namespace, field_selector)
                issue["context"]["events"] = events

                # Get pod logs for context
                if pod.status.phase != 'Pending':
                    logs = await self.get_pod_logs(pod_name, pod_namespace)
                    issue["context"]["logs"] = logs

                issues.append(issue)

            # Check container statuses
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if not container.ready:
                        if container.state.waiting:
                            reason = container.state.waiting.reason
                            message = container.state.waiting.message

                            issue = {
                                "resource_type": "container",
                                "name": container.name,
                                "pod": pod_name,
                                "namespace": pod_namespace,
                                "severity": "high" if reason in ["CrashLoopBackOff", "Error", "ImagePullBackOff"] else "medium",
                                "issue": f"Container {container.name} is waiting: {reason}",
                                "details": message,
                                "context": {}
                            }

                            # Get pod logs for context
                            logs = await self.get_pod_logs(pod_name, pod_namespace)
                            issue["context"]["logs"] = logs

                            issues.append(issue)

        # Check for deployment issues
        for name, replicas, status in deployments:
            if "Unhealthy" in status:
                # Find the deployment namespace
                deployment_namespace = None
                for pod in pods:
                    if pod.metadata.labels and pod.metadata.labels.get("app") == name:
                        deployment_namespace = pod.metadata.namespace
                        break

                if not deployment_namespace and namespace:
                    deployment_namespace = namespace

                if deployment_namespace and (not namespace or deployment_namespace == namespace):
                    issue = {
                        "resource_type": "deployment",
                        "name": name,
                        "namespace": deployment_namespace,
                        "severity": "high",
                        "issue": f"Deployment {name} is unhealthy: {status}",
                        "context": {}
                    }

                    # Get deployment events
                    field_selector = f"involvedObject.name={name}"
                    events = await self.get_events(deployment_namespace, field_selector)
                    issue["context"]["events"] = events

                    issues.append(issue)

        # Add more resource checks here

        return issues