from typing import Dict, List, Any, Optional
import re

class CommandGenerator:
    """Generate kubectl and cloud CLI commands based on user queries."""

    def __init__(self):
        """Initialize the command generator."""
        # Command templates for common operations
        self.kubectl_templates = {
            "get": "kubectl get {resource_type} {resource_name} -n {namespace} {output_format}",
            "describe": "kubectl describe {resource_type} {resource_name} -n {namespace}",
            "logs": "kubectl logs {pod_name} {container} -n {namespace} {tail} {follow}",
            "exec": "kubectl exec -it {pod_name} -n {namespace} {container} -- {command}",
            "delete": "kubectl delete {resource_type} {resource_name} -n {namespace}",
            "apply": "kubectl apply -f {filename}",
            "port-forward": "kubectl port-forward {resource_type}/{resource_name} {local_port}:{remote_port} -n {namespace}",
            "rollout": "kubectl rollout {rollout_command} {resource_type}/{resource_name} -n {namespace}",
            "scale": "kubectl scale {resource_type}/{resource_name} --replicas={replicas} -n {namespace}",
            "top": "kubectl top {resource_type} {resource_name} -n {namespace}",
            "events": "kubectl get events -n {namespace} --sort-by='.lastTimestamp' {field_selector}"
        }

        # AWS CLI templates
        self.aws_templates = {
            "eks_describe_cluster": "aws eks describe-cluster --name {cluster_name}",
            "eks_update_kubeconfig": "aws eks update-kubeconfig --name {cluster_name} --region {region}",
            "eks_list_nodegroups": "aws eks list-nodegroups --cluster-name {cluster_name}",
            "eks_describe_nodegroup": "aws eks describe-nodegroup --cluster-name {cluster_name} --nodegroup-name {nodegroup_name}",
            "ec2_describe_instances": "aws ec2 describe-instances --filters \"Name=tag:kubernetes.io/cluster/{cluster_name},Values=owned\"",
            "cloudwatch_logs": "aws logs get-log-events --log-group-name {log_group} --log-stream-name {log_stream}"
        }

        # GCP CLI templates
        self.gcp_templates = {
            "gke_get_credentials": "gcloud container clusters get-credentials {cluster_name} --zone {zone} --project {project_id}",
            "gke_describe_cluster": "gcloud container clusters describe {cluster_name} --zone {zone}",
            "gke_list_nodepools": "gcloud container node-pools list --cluster {cluster_name} --zone {zone}",
            "gke_describe_nodepool": "gcloud container node-pools describe {nodepool_name} --cluster {cluster_name} --zone {zone}"
        }

        # Azure CLI templates
        self.azure_templates = {
            "aks_get_credentials": "az aks get-credentials --resource-group {resource_group} --name {cluster_name}",
            "aks_show": "az aks show --resource-group {resource_group} --name {cluster_name}",
            "aks_nodepool_list": "az aks nodepool list --resource-group {resource_group} --cluster-name {cluster_name}",
            "aks_nodepool_show": "az aks nodepool show --resource-group {resource_group} --cluster-name {cluster_name} --name {nodepool_name}"
        }

    def generate_commands(self, query_result: Dict[str, Any], context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Generate commands based on the parsed query and context."""
        commands = []

        # Extract relevant information from the query
        intent = query_result.get("intent", {}).get("action")
        resource_types = query_result.get("entities", {}).get("resource_type", [])
        resource_names = query_result.get("entities", {}).get("resource_name", [])
        namespace = query_result.get("entities", {}).get("namespace") or context.get("current_namespace", "default")
        issue_types = query_result.get("entities", {}).get("issue_type", [])
        cloud_providers = query_result.get("entities", {}).get("cloud_provider", [])

        # Default resource name if not specified
        resource_name = resource_names[0] if resource_names else ""

        # Default resource type if not specified
        resource_type = resource_types[0] if resource_types else "pod"

        # Generate kubectl commands based on intent
        if intent == "troubleshoot":
            # Add commands for troubleshooting
            if "crash" in issue_types or not issue_types:
                if resource_type == "pod":
                    commands.append({
                        "command": self.kubectl_templates["logs"].format(
                            pod_name=resource_name or "<pod-name>",
                            container="",
                            namespace=namespace,
                            tail="--tail=100",
                            follow=""
                        ),
                        "description": f"View logs for the pod to identify errors"
                    })

                commands.append({
                    "command": self.kubectl_templates["describe"].format(
                        resource_type=resource_type,
                        resource_name=resource_name or f"<{resource_type}-name>",
                        namespace=namespace
                    ),
                    "description": f"Get detailed information about the {resource_type} including events"
                })

                commands.append({
                    "command": self.kubectl_templates["events"].format(
                        namespace=namespace,
                        field_selector=f"--field-selector involvedObject.name={resource_name}" if resource_name else ""
                    ),
                    "description": "View recent events to identify issues"
                })

            if "network" in issue_types:
                commands.append({
                    "command": f"kubectl run tmp-shell --rm -i --tty --image nicolaka/netshoot -- /bin/bash",
                    "description": "Start a temporary debugging pod with network tools"
                })

                if resource_type == "service":
                    commands.append({
                        "command": f"kubectl run tmp-shell --rm -i --tty --image nicolaka/netshoot -- curl {resource_name}.{namespace}.svc.cluster.local",
                        "description": f"Test connectivity to the service {resource_name}"
                    })

            if "performance" in issue_types:
                commands.append({
                    "command": self.kubectl_templates["top"].format(
                        resource_type=resource_type if resource_type in ["pod", "node"] else "pod",
                        resource_name=resource_name or "",
                        namespace=namespace
                    ),
                    "description": f"Check resource usage"
                })

        elif intent == "list":
            # Add commands for listing resources
            commands.append({
                "command": self.kubectl_templates["get"].format(
                    resource_type=resource_type + "s" if resource_type[-1] != 's' else resource_type,
                    resource_name="",
                    namespace=namespace,
                    output_format="-o wide"
                ),
                "description": f"List all {resource_type}s in the {namespace} namespace"
            })

            if resource_type == "pod":
                commands.append({
                    "command": f"kubectl get pods -n {namespace} --sort-by='.status.phase'",
                    "description": "List pods sorted by status"
                })

        elif intent == "explain":
            # Add commands for explaining resources
            commands.append({
                "command": f"kubectl explain {resource_type}",
                "description": f"Show documentation for {resource_type} resource"
            })

            commands.append({
                "command": f"kubectl explain {resource_type}.spec",
                "description": f"Show documentation for {resource_type} spec"
            })

            if resource_name:
                commands.append({
                    "command": self.kubectl_templates["get"].format(
                        resource_type=resource_type,
                        resource_name=resource_name,
                        namespace=namespace,
                        output_format="-o yaml"
                    ),
                    "description": f"Get YAML definition of the {resource_type}"
                })

        # Add cloud provider specific commands if applicable
        if "aws" in cloud_providers:
            cluster_name = context.get("cluster_name", "<cluster-name>")
            region = context.get("region", "<region>")

            if resource_type == "node":
                commands.append({
                    "command": self.aws_templates["eks_describe_nodegroup"].format(
                        cluster_name=cluster_name,
                        nodegroup_name=resource_name or "<nodegroup-name>"
                    ),
                    "description": "Get details about the EKS node group"
                })

            commands.append({
                "command": self.aws_templates["eks_describe_cluster"].format(
                    cluster_name=cluster_name
                ),
                "description": "Get details about the EKS cluster"
            })

        elif "gcp" in cloud_providers:
            cluster_name = context.get("cluster_name", "<cluster-name>")
            zone = context.get("zone", "<zone>")
            project_id = context.get("project_id", "<project-id>")

            if resource_type == "node":
                commands.append({
                    "command": self.gcp_templates["gke_describe_nodepool"].format(
                        cluster_name=cluster_name,
                        nodepool_name=resource_name or "<nodepool-name>",
                        zone=zone
                    ),
                    "description": "Get details about the GKE node pool"
                })

            commands.append({
                "command": self.gcp_templates["gke_describe_cluster"].format(
                    cluster_name=cluster_name,
                    zone=zone
                ),
                "description": "Get details about the GKE cluster"
            })

        elif "azure" in cloud_providers:
            cluster_name = context.get("cluster_name", "<cluster-name>")
            resource_group = context.get("resource_group", "<resource-group>")

            if resource_type == "node":
                commands.append({
                    "command": self.azure_templates["aks_nodepool_show"].format(
                        cluster_name=cluster_name,
                        resource_group=resource_group,
                        nodepool_name=resource_name or "<nodepool-name>"
                    ),
                    "description": "Get details about the AKS node pool"
                })

            commands.append({
                "command": self.azure_templates["aks_show"].format(
                    cluster_name=cluster_name,
                    resource_group=resource_group
                ),
                "description": "Get details about the AKS cluster"
            })

        return commands

    def generate_yaml_examples(self, query_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate YAML examples based on the parsed query."""
        examples = []

        # Extract relevant information from the query
        resource_types = query_result.get("entities", {}).get("resource_type", [])

        # Default resource type if not specified
        resource_type = resource_types[0] if resource_types else "pod"

        # Generate YAML examples based on resource type
        if resource_type == "pod":
            examples.append({
                "title": "Basic Pod",
                "yaml": """apiVersion: v1
kind: Pod
metadata:
  name: example-pod
  labels:
    app: example
spec:
  containers:
  - name: nginx
    image: nginx:1.19
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"
"""
            })

        elif resource_type == "deployment":
            examples.append({
                "title": "Basic Deployment",
                "yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-deployment
  labels:
    app: example
spec:
  replicas: 3
  selector:
    matchLabels:
      app: example
  template:
    metadata:
      labels:
        app: example
    spec:
      containers:
      - name: nginx
        image: nginx:1.19
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
"""
            })

        elif resource_type == "service":
            examples.append({
                "title": "Basic Service",
                "yaml": """apiVersion: v1
kind: Service
metadata:
  name: example-service
spec:
  selector:
    app: example
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
"""
            })

        elif resource_type == "ingress":
            examples.append({
                "title": "Basic Ingress",
                "yaml": """apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: example-service
            port:
              number: 80
"""
            })

        # Add more resource types as needed

        return examples