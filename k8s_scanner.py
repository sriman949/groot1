"""Kubernetes scanner for Groot CLI."""

import asyncio
import json
import re
import os
from typing import List, Dict, Any, Tuple, Optional

try:
    from kubernetes import client, config as k8s_config
    from kubernetes.client.rest import ApiException
    k8s_available = True
except ImportError:
    k8s_available = False

from rich.console import Console
from groot.utils.helpers import format_age
from groot.config import config as groot_config

console = Console()

class K8sScanner:
    """Scanner for Kubernetes resources."""

    def __init__(self):
        """Initialize the Kubernetes scanner."""
        self.initialized = False
        self.v1 = None
        self.apps_v1 = None
        self.custom_api = None

    async def initialize(self):
        """Initialize the Kubernetes client."""
        if self.initialized:
            return

        if not k8s_available:
            console.print("[red]Kubernetes client not available. Please install kubernetes package.[/red]")
            return

        try:
            # Load kubeconfig
            k8s_config.load_kube_config()

            # Create API clients
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.custom_api = client.CustomObjectsApi()

            self.initialized = True
        except Exception as e:
            console.print(f"[red]Error initializing Kubernetes client: {e}[/red]")

    async def get_pods(self, namespace: str = None) -> List[Any]:
        """Get pods from the cluster."""
        await self.initialize()

        if not self.initialized:
            return []

        try:
            if namespace and namespace != "all":
                pods = self.v1.list_namespaced_pod(namespace)
            else:
                pods = self.v1.list_pod_for_all_namespaces()

            return pods.items
        except ApiException as e:
            console.print(f"[red]Error getting pods: {e}[/red]")
            return []

    async def get_deployments(self) -> List[Tuple[str, int, str]]:
        """Get deployments from the cluster."""
        await self.initialize()

        if not self.initialized:
            return []

        try:
            deployments = self.apps_v1.list_deployment_for_all_namespaces()

            result = []
            for deployment in deployments.items:
                name = deployment.metadata.name
                replicas = deployment.spec.replicas

                # Check if deployment is healthy
                available = deployment.status.available_replicas or 0
                desired = deployment.status.replicas or 0

                if desired == 0:
                    status = "No replicas desired"
                elif available == desired:
                    status = f"Healthy ({available}/{desired} replicas)"
                else:
                    status = f"Unhealthy ({available}/{desired} replicas)"

                result.append((name, replicas, status))

            return result
        except ApiException as e:
            console.print(f"[red]Error getting deployments: {e}[/red]")
            return []

    async def get_services(self) -> List[Tuple[str, str]]:
        """Get services from the cluster."""
        await self.initialize()

        if not self.initialized:
            return []

        try:
            services = self.v1.list_service_for_all_namespaces()

            result = []
            for service in services.items:
                name = service.metadata.name
                service_type = service.spec.type

                result.append((name, service_type))

            return result
        except ApiException as e:
            console.print(f"[red]Error getting services: {e}[/red]")
            return []

    async def get_namespaces(self) -> List[str]:
        """Get namespaces from the cluster."""
        await self.initialize()

        if not self.initialized:
            return ["default"]

        try:
            namespaces = self.v1.list_namespace()

            return [ns.metadata.name for ns in namespaces.items]
        except ApiException as e:
            console.print(f"[red]Error getting namespaces: {e}[/red]")
            return ["default"]

    async def get_pod_logs(self, pod_name: str, namespace: str, container: str = None, tail_lines: int = 100) -> str:
        """Get logs for a pod."""
        await self.initialize()

        if not self.initialized:
            return "Error: Kubernetes client not initialized"

        try:
            if container:
                logs = self.v1.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    container=container,
                    tail_lines=tail_lines
                )
            else:
                logs = self.v1.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    tail_lines=tail_lines
                )

            return logs
        except ApiException as e:
            if e.status == 404:
                return f"Error: Pod {pod_name} not found in namespace {namespace}"
            else:
                return f"Error getting logs: {e}"

    async def get_events(self, namespace: str, field_selector: str = None) -> List[Dict[str, Any]]:
        """Get events from the cluster."""
        await self.initialize()

        if not self.initialized:
            return []

        try:
            if namespace and namespace != "all":
                events = self.v1.list_namespaced_event(
                    namespace=namespace,
                    field_selector=field_selector,
                    sort_by="lastTimestamp"
                )
            else:
                events = self.v1.list_event_for_all_namespaces(
                    field_selector=field_selector,
                    sort_by="lastTimestamp"
                )

            # Convert to dict for easier handling
            result = []
            for event in events.items:
                event_dict = {
                    "type": event.type,
                    "reason": event.reason,
                    "message": event.message,
                    "count": event.count,
                    "firstTimestamp": event.first_timestamp,
                    "lastTimestamp": event.last_timestamp,
                    "involvedObject": {
                        "kind": event.involved_object.kind,
                        "name": event.involved_object.name,
                        "namespace": event.involved_object.namespace
                    }
                }
                result.append(event_dict)

            return result
        except ApiException as e:
            console.print(f"[red]Error getting events: {e}[/red]")
            return []

    async def describe_resource(self, resource_type: str, name: str, namespace: str) -> Dict[str, Any]:
        """Describe a Kubernetes resource."""
        await self.initialize()

        if not self.initialized:
            return {"error": "Kubernetes client not initialized"}

        try:
            if resource_type == "pod":
                resource = self.v1.read_namespaced_pod(name=name, namespace=namespace)
            elif resource_type == "deployment":
                resource = self.apps_v1.read_namespaced_deployment(name=name, namespace=namespace)
            elif resource_type == "service":
                resource = self.v1.read_namespaced_service(name=name, namespace=namespace)
            elif resource_type == "configmap":
                resource = self.v1.read_namespaced_config_map(name=name, namespace=namespace)
            elif resource_type == "secret":
                resource = self.v1.read_namespaced_secret(name=name, namespace=namespace)
            elif resource_type == "ingress":
                networking_v1 = client.NetworkingV1Api()
                resource = networking_v1.read_namespaced_ingress(name=name, namespace=namespace)
            else:
                return {"error": f"Unsupported resource type: {resource_type}"}

            # Convert to dict for easier handling
            return self._convert_k8s_obj_to_dict(resource)
        except ApiException as e:
            if e.status == 404:
                return {"error": f"{resource_type.capitalize()} {name} not found in namespace {namespace}"}
            else:
                return {"error": f"Error describing {resource_type}: {e}"}

    def _convert_k8s_obj_to_dict(self, obj) -> Dict[str, Any]:
        """Convert Kubernetes object to dictionary."""
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return obj
        elif isinstance(obj, list):
            return [self._convert_k8s_obj_to_dict(item) for item in obj]
        else:
            return obj

    async def analyze_resources(self, namespace: str) -> List[Dict[str, Any]]:
        """Analyze resources in a namespace for issues."""
        await self.initialize()

        if not self.initialized:
            return []

        issues = []

        # Get pods
        pods = await self.get_pods(namespace)

        # Check for pod issues
        for pod in pods:
            # Check for crash loop backoff
            if pod.status.phase != "Running":
                if pod.status.container_statuses:
                    for container in pod.status.container_statuses:
                        if container.state.waiting and container.state.waiting.reason == "CrashLoopBackOff":
                            issues.append({
                                "resource_type": "pod",
                                "name": pod.metadata.name,
                                "severity": "high",
                                "issue": "Pod is in CrashLoopBackOff state",
                                "details": f"Container {container.name} is crashing repeatedly. Check logs for more information."
                            })
                        elif container.state.waiting and container.state.waiting.reason == "ImagePullBackOff":
                            issues.append({
                                "resource_type": "pod",
                                "name": pod.metadata.name,
                                "severity": "high",
                                "issue": "Pod is in ImagePullBackOff state",
                                "details": f"Container {container.name} image cannot be pulled. Check image name and registry access."
                            })

            # Check for high restart count
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    if container.restart_count > 10:
                        issues.append({
                            "resource_type": "pod",
                            "name": pod.metadata.name,
                            "severity": "medium",
                            "issue": "Container has high restart count",
                            "details": f"Container {container.name} has restarted {container.restart_count} times. Check logs for more information."
                        })

            # Check for missing resource limits
            if pod.spec.containers:
                for container in pod.spec.containers:
                    if not container.resources or not container.resources.limits:
                        issues.append({
                            "resource_type": "pod",
                            "name": pod.metadata.name,
                            "severity": "low",
                            "issue": "Container missing resource limits",
                            "details": f"Container {container.name} does not have resource limits set. This can lead to resource contention."
                        })

        # Get deployments
        try:
            deployments = self.apps_v1.list_namespaced_deployment(namespace=namespace)

            # Check for deployment issues
            for deployment in deployments.items:
                # Check for unavailable replicas
                if deployment.status.unavailable_replicas:
                    issues.append({
                        "resource_type": "deployment",
                        "name": deployment.metadata.name,
                        "severity": "medium",
                        "issue": "Deployment has unavailable replicas",
                        "details": f"Deployment has {deployment.status.unavailable_replicas} unavailable replicas out of {deployment.spec.replicas} desired."
                    })

                # Check for missing pod anti-affinity
                if not deployment.spec.template.spec.affinity or not deployment.spec.template.spec.affinity.pod_anti_affinity:
                    issues.append({
                        "resource_type": "deployment",
                        "name": deployment.metadata.name,
                        "severity": "low",
                        "issue": "Deployment missing pod anti-affinity",
                        "details": "Pod anti-affinity is not configured. This can lead to all pods running on the same node."
                    })

        except ApiException as e:
            console.print(f"[red]Error analyzing deployments: {e}[/red]")

        # Get services
        try:
            services = self.v1.list_namespaced_service(namespace=namespace)

            # Check for service issues
            for service in services.items:
                # Check for services without endpoints
                try:
                    endpoints = self.v1.read_namespaced_endpoints(name=service.metadata.name, namespace=namespace)
                    if not endpoints.subsets or not any(subset.addresses for subset in endpoints.subsets):
                        issues.append({
                            "resource_type": "service",
                            "name": service.metadata.name,
                            "severity": "medium",
                            "issue": "Service has no endpoints",
                            "details": "Service selector does not match any pods. Check pod labels and service selector."
                        })
                except ApiException:
                    pass

        except ApiException as e:
            console.print(f"[red]Error analyzing services: {e}[/red]")

        return issues