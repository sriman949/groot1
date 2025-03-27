import spacy
import re
from typing import Dict, List, Tuple, Any
from rich.console import Console

console = Console()

class NLPEngine:
    """Enhanced NLP engine for understanding cloud and Kubernetes queries."""

    def __init__(self):
        # Load more comprehensive NLP model
        try:
            self.nlp = spacy.load('en_core_web_lg')  # Larger model with better semantics
        except OSError:
            console.print("[yellow]Downloading enhanced language model...[/yellow]")
            spacy.cli.download('en_core_web_lg')
            self.nlp = spacy.load('en_core_web_lg')

        # Load custom entity patterns for Kubernetes and cloud terms
        self.add_custom_entities()

        # Common Kubernetes/cloud action patterns
        self.action_patterns = {
            "troubleshoot": ["fix", "solve", "troubleshoot", "debug", "diagnose", "resolve"],
            "explain": ["explain", "describe", "tell me about", "what is", "how does", "why is"],
            "list": ["list", "show", "get", "find", "display"],
            "create": ["create", "make", "deploy", "launch", "start"],
            "delete": ["delete", "remove", "destroy", "take down"],
            "update": ["update", "change", "modify", "edit", "patch"],
            "compare": ["compare", "diff", "difference", "versus", "vs"]
        }

        # Resource type patterns
        self.resource_patterns = {
            "pod": ["pod", "pods", "container"],
            "deployment": ["deployment", "deploy", "deployments"],
            "service": ["service", "svc", "services"],
            "ingress": ["ingress", "ing", "ingresses"],
            "configmap": ["configmap", "cm", "config map", "configmaps"],
            "secret": ["secret", "secrets"],
            "node": ["node", "nodes", "machine", "instance"],
            "namespace": ["namespace", "ns", "namespaces"],
            "pv": ["persistent volume", "pv", "volume"],
            "pvc": ["persistent volume claim", "pvc", "volume claim"],
            "statefulset": ["statefulset", "sts", "stateful set"],
            "daemonset": ["daemonset", "ds", "daemon set"],
            "job": ["job", "jobs", "batch job"],
            "cronjob": ["cronjob", "cron job", "scheduled job"]
        }

        # Cloud provider patterns
        self.cloud_patterns = {
            "aws": ["aws", "amazon", "ec2", "s3", "rds", "dynamodb", "lambda"],
            "gcp": ["gcp", "google cloud", "gke", "cloud storage", "bigquery"],
            "azure": ["azure", "aks", "microsoft", "blob storage"]
        }

        # Common issue patterns
        self.issue_patterns = {
            "crash": ["crash", "crashing", "crashloopbackoff", "restarting", "failing"],
            "network": ["network", "connectivity", "connection", "cannot connect", "unreachable"],
            "performance": ["slow", "performance", "latency", "throughput", "cpu", "memory"],
            "storage": ["storage", "volume", "disk", "persistent volume", "pv", "pvc"],
            "security": ["security", "permission", "rbac", "access", "unauthorized", "forbidden"],
            "scaling": ["scale", "scaling", "autoscale", "hpa", "vpa", "resize"],
            "configuration": ["config", "configuration", "misconfigured", "setting", "parameter"]
        }

    def add_custom_entities(self):
        """Add custom entity recognition for Kubernetes and cloud terms."""
        # Create entity ruler to identify Kubernetes and cloud terms
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")

        # Add Kubernetes resource patterns
        patterns = [
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "pod"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "pods"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "deployment"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "service"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "ingress"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "configmap"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "secret"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "namespace"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "node"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "statefulset"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "daemonset"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "job"}]},
            {"label": "K8S_RESOURCE", "pattern": [{"LOWER": "cronjob"}]},

            # Cloud resources
            {"label": "CLOUD_RESOURCE", "pattern": [{"LOWER": "ec2"}]},
            {"label": "CLOUD_RESOURCE", "pattern": [{"LOWER": "s3"}]},
            {"label": "CLOUD_RESOURCE", "pattern": [{"LOWER": "rds"}]},
            {"label": "CLOUD_RESOURCE", "pattern": [{"LOWER": "lambda"}]},
            {"label": "CLOUD_RESOURCE", "pattern": [{"LOWER": "gke"}]},
            {"label": "CLOUD_RESOURCE", "pattern": [{"LOWER": "aks"}]},

            # Common Kubernetes errors
            {"label": "K8S_ERROR", "pattern": [{"LOWER": "crashloopbackoff"}]},
            {"label": "K8S_ERROR", "pattern": [{"LOWER": "imagepullbackoff"}]},
            {"label": "K8S_ERROR", "pattern": [{"LOWER": "oomkilled"}]},
            {"label": "K8S_ERROR", "pattern": [{"LOWER": "evicted"}]},
            {"label": "K8S_ERROR", "pattern": [{"LOWER": "pending"}]},
        ]

        ruler.add_patterns(patterns)

    def parse  "pending"}]},
    ]

    ruler.add_patterns(patterns)

    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse a natural language query to extract intent and entities."""
        doc = self.nlp(query.lower())

        # Initialize result
        result = {
            "original_query": query,
            "intent": {
                "action": None,
                "confidence": 0.0
            },
            "entities": {
                "resource_type": [],
                "resource_name": [],
                "namespace": None,
                "cloud_provider": [],
                "issue_type": [],
                "time_period": None,
                "count": None
            },
            "context": {
                "is_question": False,
                "requires_explanation": False,
                "requires_code": False,
                "requires_comparison": False
            }
        }

        # Check if it's a question
        result["context"]["is_question"] = any(token.text in ["what", "why", "how", "when", "where", "which", "who"] for token in doc) or query.endswith("?")

        # Detect intent (action)
        for action, patterns in self.action_patterns.items():
            for pattern in patterns:
                if pattern in query.lower():
                    result["intent"]["action"] = action
                    result["intent"]["confidence"] = 0.8
                    break
            if result["intent"]["action"]:
                break

        # If no explicit action found, infer from context
        if not result["intent"]["action"]:
            if result["context"]["is_question"]:
                if any(token.text in ["what", "why", "how"] for token in doc):
                    result["intent"]["action"] = "explain"
                    result["context"]["requires_explanation"] = True
                elif any(token.text in ["where", "which", "list", "show", "find"] for token in doc):
                    result["intent"]["action"] = "list"
            else:
                # Default to troubleshoot for statements about issues
                for issue_type, patterns in self.issue_patterns.items():
                    if any(pattern in query.lower() for pattern in patterns):
                        result["intent"]["action"] = "troubleshoot"
                        result["entities"]["issue_type"].append(issue_type)
                        break

        # Extract resource types
        for resource, patterns in self.resource_patterns.items():
            if any(pattern in query.lower() for pattern in patterns):
                result["entities"]["resource_type"].append(resource)

        # Extract cloud providers
        for provider, patterns in self.cloud_patterns.items():
            if any(pattern in query.lower() for pattern in patterns):
                result["entities"]["cloud_provider"].append(provider)

        # Extract issue types if not already done
        if not result["entities"]["issue_type"]:
            for issue, patterns in self.issue_patterns.items():
                if any(pattern in query.lower() for pattern in patterns):
                    result["entities"]["issue_type"].append(issue)

        # Extract resource names (look for quoted strings or words after resource types)
        # Look for quoted strings first
        quoted_names = re.findall(r'"([^"]*)"', query) + re.findall(r"'([^']*)'", query)
        if quoted_names:
            result["entities"]["resource_name"] = quoted_names
        else:
            # Look for words after resource types
            for resource_type in result["entities"]["resource_type"]:
                patterns = self.resource_patterns[resource_type]
                for pattern in patterns:
                    match = re.search(f"{pattern} ([a-zA-Z0-9-]+)", query.lower())
                    if match:
                        result["entities"]["resource_name"].append(match.group(1))

        # Extract namespace
        namespace_match = re.search(r"(?:in|from|namespace|ns) ([a-zA-Z0-9-]+)", query.lower())
        if namespace_match:
            result["entities"]["namespace"] = namespace_match.group(1)

        # Check if code is required
        if any(word in query.lower() for word in ["command", "kubectl", "code", "yaml", "script", "how to", "steps to"]):
            result["context"]["requires_code"] = True

        # Check if comparison is required
        if any(word in query.lower() for word in ["compare", "difference", "versus", "vs", "better", "preferred"]):
            result["context"]["requires_comparison"] = True
            result["intent"]["action"] = "compare"

        # Extract time periods
        time_match = re.search(r"(?:in the last|past|previous|recent) ([0-9]+) (minute|minutes|hour|hours|day|days|week|weeks|month|months)", query.lower())
        if time_match:
            result["entities"]["time_period"] = {
                "value": int(time_match.group(1)),
                "unit": time_match.group(2)
            }

        # Extract counts
        count_match = re.search(r"(?:top|first|last) ([0-9]+)", query.lower())
        if count_match:
            result["entities"]["count"] = int(count_match.group(1))

        return result

    def generate_follow_up_questions(self, query_result: Dict[str, Any], k8s_context: Dict[str, Any]) -> List[str]:
        """Generate relevant follow-up questions based on the query and context."""
        follow_ups = []

        # If troubleshooting with no specific resource
        if query_result["intent"]["action"] == "troubleshoot" and not query_result["entities"]["resource_type"]:
            follow_ups.append("Which specific resources are you having issues with?")

        # If resource type but no name
        if query_result["entities"]["resource_type"] and not query_result["entities"]["resource_name"]:
            resource_type = query_result["entities"]["resource_type"][0]
            follow_ups.append(f"Which specific {resource_type} are you interested in?")

        # If no namespace specified
        if not query_result["entities"]["namespace"] and k8s_context.get("namespaces", []) and len(k8s_context["namespaces"]) > 1:
            follow_ups.append("Which namespace should I focus on?")

        # If performance issue with no specifics
        if "performance" in query_result["entities"]["issue_type"] and not query_result["entities"]["resource_name"]:
            follow_ups.append("Are you seeing high CPU usage, memory usage, or slow response times?")

        # If network issue
        if "network" in query_result["entities"]["issue_type"]:
            follow_ups.append("Are you having issues with internal or external connectivity?")

        # If security issue
        if "security" in query_result["entities"]["issue_type"]:
            follow_ups.append("Are you seeing permission errors or authentication issues?")

        # Limit to 3 follow-up questions
        return follow_ups[:3]