# groot/cli.py
import asyncio
import sys
import os
import json
import argparse
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import box
import click

from groot.k8s_scanner import K8sScanner
from groot.ai_assistant import AIAssistant
from groot.nlp_engine import NLPEngine
from groot.config import config

console = Console()

class GrootCLI:
    """Enhanced Groot CLI with comprehensive Kubernetes troubleshooting capabilities."""

    def __init__(self):
        self.running = True
        self.scanner = K8sScanner()
        self.ai_assistant = AIAssistant()
        self.nlp_engine = NLPEngine()
        self.current_namespace = config.get("default_namespace", "default")
        self.cluster_context = {}

    def greet(self):
        """Display welcome message."""
        console.print(Panel.fit(
            "[bold green]I am Groot - Advanced Kubernetes & Cloud Troubleshooting Assistant[/bold green]\n\n"
            "Type [bold cyan]help[/bold cyan] to see available commands or ask me anything about your Kubernetes cluster or cloud infrastructure.",
            title="🌱 Groot 🌱",
            border_style="green"
        ))

    def print_help(self):
        """Display help information."""
        help_table = Table(title="Groot Commands", border_style="cyan", box=box.ROUNDED)
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description")

        help_table.add_row("status", "Show cluster status overview")
        help_table.add_row("scan namespace [name]", "Scan resources in a namespace")
        help_table.add_row("analyze [resource] [name]", "Analyze a specific resource")
        help_table.add_row("custom-resource [type] [name]", "Analyze a custom resource")
        help_table.add_row("logs [pod] [namespace]", "Get logs for a pod")
        help_table.add_row("events [namespace]", "Get events in a namespace")
        help_table.add_row("explain [concept]", "Explain a Kubernetes concept")
        help_table.add_row("compare [resource1] [resource2]", "Compare two Kubernetes resources")
        help_table.add_row("best-practices [resource]", "Show best practices for a resource")
        help_table.add_row("set-namespace [name]", "Set default namespace")
        help_table.add_row("help", "Show this help message")
        help_table.add_row("exit", "Exit Groot")

        console.print(help_table)
        console.print("\n[bold green]Natural Language Queries:[/bold green]")
        console.print("You can also ask me questions in natural language like:")
        console.print("  • \"Why are my pods crashing in the production namespace?\"")
        console.print("  • \"How do I troubleshoot network connectivity issues between services?\"")
        console.print("  • \"What's the difference between a Deployment and a StatefulSet?\"")
        console.print("  • \"Show me how to set up an Ingress with TLS\"")

    async def process_command(self, command: str) -> str:
        """Process a command and return the result."""
        parts = command.split()

        if not parts:
            return "Please enter a command or question."

        cmd = parts[0].lower()

        if cmd == "help":
            self.print_help()
            return ""

        elif cmd == "status":
            return await self.check_k8s_status()

        elif cmd == "scan" and len(parts) >= 2:
            resource_type = parts[1]
            name = parts[2] if len(parts) > 2 else self.current_namespace

            if resource_type == "namespace":
                return await self.scan_namespace(name)
            else:
                return f"Unknown resource type: {resource_type}"

        elif cmd == "analyze" and len(parts) >= 3:
            resource_type = parts[1]
            name = parts[2]
            namespace = parts[3] if len(parts) > 3 else self.current_namespace

            return await self.analyze_resource(resource_type, name, namespace)

        elif cmd == "logs" and len(parts) >= 2:
            pod = parts[1]
            namespace = parts[2] if len(parts) > 2 else self.current_namespace

            return await self.get_pod_logs(pod, namespace)

        elif cmd == "events" and len(parts) >= 1:
            namespace = parts[1] if len(parts) > 1 else self.current_namespace

            return await self.get_namespace_events(namespace)

        elif cmd == "explain" and len(parts) >= 2:
            concept = " ".join(parts[1:])
            return await self.explain_concept(concept)

        elif cmd == "compare" and len(parts) >= 3:
            resource1 = parts[1]
            resource2 = parts[2]
            return await self.compare_resources(resource1, resource2)

        elif cmd == "best-practices" and len(parts) >= 2:
            resource = parts[1]
            return await self.show_best_practices(resource)

        elif cmd == "set-namespace" and len(parts) >= 2:
            self.current_namespace = parts[1]
            config.set("default_namespace", self.current_namespace)
            return f"Default namespace set to: {self.current_namespace}"

        elif cmd == "exit":
            return self.exit_program()

        else:
            # Treat as natural language query
            return await self.process_nl_query(command)

    async def check_k8s_status(self):
        """Retrieve and display the status of Kubernetes resources in a table format."""
        with console.status("[cyan]Checking Kubernetes resource status...", spinner="dots"):
            # Get resources
            pods = await self.scanner.get_pods()
            deployments = await self.scanner.get_deployments()
            services = await self.scanner.get_services()
            namespaces = await self.scanner.get_namespaces()

            # Update cluster context
            self.cluster_context = {
                "namespaces": namespaces,
                "pod_count": len(pods),
                "deployment_count": len(deployments),
                "service_count": len(services)
            }

        # Namespaces table
        ns_table = Table(title="📁 Namespaces", border_style="green", box=box.ROUNDED)
        ns_table.add_column("Namespace")

        for ns in namespaces:
            ns_table.add_row(ns)

        console.print(ns_table)

        # Pods table
        pod_table = Table(title="📦 Pods", border_style="green", box=box.ROUNDED)
        pod_table.add_column("Pod")
        pod_table.add_column("Namespace")
        pod_table.add_column("Status")
        pod_table.add_column("Restarts", justify="right")
        pod_table.add_column("Age")

        # Count pod statuses
        status_counts = {"Running": 0, "Pending": 0, "Failed": 0, "Succeeded": 0, "Unknown": 0}

        for pod in pods:
            status = pod.status.phase
            status_counts[status] = status_counts.get(status, 0) + 1

            status_style = "green" if status == "Running" else "yellow" if status == "Pending" else "red"

            # Get restart count
            restarts = 0
            if pod.status.container_statuses:
                for container in pod.status.container_statuses:
                    restarts += container.restart_count

            # Calculate age
            age = "Unknown"
            if pod.metadata.creation_timestamp:
                import datetime
                now = datetime.datetime.now(pod.metadata.creation_timestamp.tzinfo)
                delta = now - pod.metadata.creation_timestamp
                days = delta.days
                hours, remainder = divmod(delta.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                if days > 0:
                    age = f"{days}d"
                elif hours > 0:
                    age = f"{hours}h"
                else:
                    age = f"{minutes}m"

            pod_table.add_row(
                pod.metadata.name,
                pod.metadata.namespace,
                f"[{status_style}]{status}[/{status_style}]",
                str(restarts),
                age
            )

        console.print(pod_table)

        # Pod status summary
        status_table = Table(title="Pod Status Summary", border_style="cyan", box=box.ROUNDED)
        status_table.add_column("Status")
        status_table.add_column("Count", justify="right")
        status_table.add_column("Percentage", justify="right")

        total_pods = len(pods)
        for status, count in status_counts.items():
            percentage = (count / total_pods * 100) if total_pods > 0 else 0
            status_style = "green" if status == "Running" else "yellow" if status == "Pending" else "red"

            status_table.add_row(
                f"[{status_style}]{status}[/{status_style}]",
                str(count),
                f"{percentage:.1f}%"
            )

        console.print(status_table)

        # Deployments table
        deploy_table = Table(title="🚀 Deployments", border_style="green", box=box.ROUNDED)
        deploy_table.add_column("Deployment")
        deploy_table.add_column("Namespace")
        deploy_table.add_column("Replicas", justify="right")
        deploy_table.add_column("Status")

        for name, replicas, status in deployments:
            # Extract namespace from pods
            namespace = "unknown"
            for pod in pods:
                if pod.metadata.labels and pod.metadata.labels.get("app") == name:
                    namespace = pod.metadata.namespace
                    break

            status_style = "green" if "Healthy" in status else "red"

            deploy_table.add_row(
                name,
                namespace,
                str(replicas),
                f"[{status_style}]{status}[/{status_style}]"
            )

        console.print(deploy_table)

        # Services table
        service_table = Table(title="🔌 Services", border_style="green", box=box.ROUNDED)
        service_table.add_column("Service")
        service_table.add_column("Namespace")
        service_table.add_column("Type")
        service_table.add_column("Cluster IP")
        service_table.add_column("External IP")

        for svc, svc_type in services:
            # Extract additional info
            namespace = "unknown"
            cluster_ip = "None"
            external_ip = "None"

            # This is a simplification - in a real implementation, we'd get this from the service object

            service_table.add_row(svc, namespace, svc_type, cluster_ip, external_ip)

        console.print(service_table)

        return ""  # Return empty string since we printed directly

    async def scan_namespace(self, namespace: str) -> str:
        """Scan a namespace for issues."""
        with console.status(f"[cyan]Scanning namespace {namespace}...", spinner="dots"):
            # Analyze resources
            issues = await self.scanner.analyze_resources(namespace)

        if not issues:
            console.print(f"[green]✅ No issues found in namespace: {namespace}[/green]")
            return ""

        # Format issues
        console.print(f"[yellow]🔍 Issues found in namespace: {namespace}[/yellow]")

        for i, issue in enumerate(issues):
            severity = issue.get("severity", "medium")
            severity_color = "red" if severity == "high" else "yellow" if severity == "medium" else "blue"

            issue_panel = Panel(
                f"[bold]Resource:[/bold] {issue['resource_type']}/{issue['name']}\n"
                f"[bold]Severity:[/bold] [{severity_color}]{severity.upper()}[/{severity_color}]\n"
                f"[bold]Issue:[/bold] {issue['issue']}\n"
                + (f"[bold]Details:[/bold] {issue['details']}\n" if "details" in issue else ""),
                title=f"Issue {i+1}",
                border_style=severity_color,
                box=box.ROUNDED
            )
            console.print(issue_panel)

        # Get AI explanation
        with console.status("[cyan]Getting AI analysis...", spinner="dots"):
            # Prepare query for AI assistant
            query = f"Analyze these issues in namespace {namespace}: " + json.dumps([{
                "resource_type": issue["resource_type"],
                "name": issue["name"],
                "issue": issue["issue"],
                "details": issue.get("details", "")
            } for issue in issues])

            response = await self.ai_assistant.process_query(query, {
                "current_namespace": namespace,
                "issues": issues
            })

        if response and "ai_response" in response:
            console.print(Panel(
                Markdown(response["ai_response"]),
                title="🤖 Groot's Analysis",
                border_style="green",
                box=box.ROUNDED
            ))

            # Show suggested commands
            if response.get("commands"):
                cmd_table = Table(title="Suggested Commands", border_style="cyan", box=box.ROUNDED)
                cmd_table.add_column("Command", style="cyan")
                cmd_table.add_column("Description")

                for cmd in response["commands"]:
                    cmd_table.add_row(cmd["command"], cmd["description"])

                console.print(cmd_table)

            # Show follow-up questions
            if response.get("follow_up_questions"):
                console.print("\n[bold cyan]Follow-up questions you might want to ask:[/bold cyan]")
                for i, question in enumerate(response["follow_up_questions"]):
                    console.print(f"  {i+1}. {question}")

        return ""  # Return empty string since we printed directly

    async def analyze_resource(self, resource_type: str, name: str, namespace: str) -> str:
        """Analyze a specific resource."""
        with console.status(f"[cyan]Analyzing {resource_type}/{name}...", spinner="dots"):
            # Get resource details
            resource_data = await self.scanner.describe_resource(resource_type, name, namespace)

            if "error" in resource_data:
                return f"[red]{resource_data['error']}[/red]"

            # Get related events
            field_selector = f"involvedObject.name={name}"
            events = await self.scanner.get_events(namespace, field_selector)

            # Prepare context for AI
            context = {
                "resource": resource_data,
                "events": events,
                "resource_type": resource_type,
                "resource_name": name,
                "namespace": namespace
            }

            # If it's a pod, get logs
            if resource_type == "pod":
                logs = await self.scanner.get_pod_logs(name, namespace)
                context["logs"] = logs

            # Prepare query for AI assistant
            query = f"Analyze this Kubernetes {resource_type} named '{name}' in namespace '{namespace}'. Identify any issues, misconfigurations, or potential improvements."

            response = await self.ai_assistant.process_query(query, context)

        # Format response
        console.print(f"[green]📊 Analysis of {resource_type}/{name}:[/green]")

        # Add events summary
        if events:
            events_table = Table(title="Recent Events", border_style="yellow", box=box.ROUNDED)
            events_table.add_column("Type")
            events_table.add_column("Reason")
            events_table.add_column("Message")
            events_table.add_column("Age")

            for event in events[:5]:  # Show only the 5 most recent events
                event_type = event.get("type", "")
                reason = event.get("reason", "")
                message = event.get("message", "")
                age = event.get("lastTimestamp", "")

                events_table.add_row(event_type, reason, message, str(age))

            console.print(events_table)

        # Add AI analysis
        if response and "ai_response" in response:
            console.print(Panel(
                Markdown(response["ai_response"]),
                title="🤖 Groot's Analysis",
                border_style="green",
                box=box.ROUNDED
            ))

            # Show suggested commands
            if response.get("commands"):
                cmd_table = Table(title="Suggested Commands", border_style="cyan", box=box.ROUNDED)
                cmd_table.add_column("Command", style="cyan")
                cmd_table.add_column("Description")

                for cmd in response["commands"]:
                    cmd_table.add_row(cmd["command"], cmd["description"])

                console.print(cmd_table)

            # Show YAML examples if any
            if response.get("yaml_examples"):
                for example in response["yaml_examples"]:
                    console.print(f"\n[bold cyan]{example['title']}:[/bold cyan]")
                    console.print(Syntax(example["yaml"], "yaml", theme="monokai"))

            # Show follow-up questions
            if response.get("follow_up_questions"):
                console.print("\n[bold cyan]Follow-up questions you might want to ask:[/bold cyan]")
                for i, question in enumerate(response["follow_up_questions"]):
                    console.print(f"  {i+1}. {question}")

        return ""  # Return empty string since we printed directly

    async def get_pod_logs(self, pod_name: str, namespace: str) -> str:
        """Get logs for a specific pod."""
        with console.status(f"[cyan]Getting logs for pod {pod_name}...", spinner="dots"):
            logs = await self.scanner.get_pod_logs(pod_name, namespace)

        console.print(f"[green]📜 Logs for pod {pod_name}:[/green]")
        console.print(Panel(logs, border_style="blue", box=box.ROUNDED))

        return ""  # Return empty string since we printed directly

    async def get_namespace_events(self, namespace: str) -> str:
        """Get events for a namespace."""
        with console.status(f"[cyan]Getting events for namespace {namespace}...", spinner="dots"):
            events = await self.scanner.get_events(namespace)

        if not events:
            return f"[yellow]No events found in namespace {namespace}[/yellow]"

        events_table = Table(title=f"📅 Events in namespace {namespace}", border_style="green", box=box.ROUNDED)
        events_table.add_column("Type")
        events_table.add_column("Kind")
        events_table.add_column("Name")
        events_table.add_column("Reason")
        events_table.add_column("Message")
        events_table.add_column("Age")

        for event in events:
            event_type = event.get("type", "")
            reason = event.get("reason", "")
            message = event.get("message", "")
            age = event.get("lastTimestamp", "")
            object_kind = event.get("involvedObject", {}).get("kind", "")
            object_name = event.get("involvedObject", {}).get("name", "")

            events_table.add_row(
                event_type,
                object_kind,
                object_name,
                reason,
                message,
                str(age)
            )

        console.print(events_table)

        return ""  # Return empty string since we printed directly

    async def explain_concept(self, concept: str) -> str:
        """Explain a Kubernetes concept."""
        with console.status(f"[cyan]Explaining {concept}...", spinner="dots"):
            explanation = await self.ai_assistant.explain_k8s_concept(concept)

        console.print(Panel(
            Markdown(explanation),
            title=f"📚 {concept.title()}",
            border_style="green",
            box=box.ROUNDED
        ))

        return ""

    async def compare_resources(self, resource1: str, resource2: str) -> str:
        """Compare two Kubernetes resources."""
        with console.status(f"[cyan]Comparing {resource1} and {resource2}...", spinner="dots"):
            comparison = await self.ai_assistant.compare_resources(resource1, resource2)

        console.print(Panel(
            Markdown(comparison),
            title=f"🔄 {resource1} vs {resource2}",
            border_style="green",
            box=box.ROUNDED
        ))

        return ""

    async def show_best_practices(self, resource: str) -> str:
        """Show best practices for a resource."""
        with console.status(f"[cyan]Finding best practices for {resource}...", spinner="dots"):
            best_practices = await self.ai_assistant.suggest_best_practices(resource)

        if not best_practices:
            return f"[yellow]No best practices found for {resource}[/yellow]"

        console.print(f"[green]🏆 Best Practices for {resource}:[/green]")

        for i, practice in enumerate(best_practices):
            console.print(Panel(
                Markdown(practice.get("content", "")),
                title=practice.get("title", f"Best Practice {i+1}"),
                border_style="cyan",
                box=box.ROUNDED
            ))

            # Show examples if any
            if "examples" in practice:
                for example in practice["examples"]:
                    console.print(f"\n[bold cyan]{example['title']}:[/bold cyan]")
                    console.print(Syntax(example["yaml"], "yaml", theme="monokai"))

        return ""

    async def process_nl_query(self, query: str) -> str:
        """Process a natural language query."""
        with console.status(f"[cyan]Processing query: {query}", spinner="dots"):
            # Get basic cluster info for context
            try:
                k8s_context = {
                    "current_namespace": self.current_namespace,
                    "namespaces": await self.scanner.get_namespaces(),
                    "pod_count": len(await self.scanner.get_pods()),
                    "deployment_count": len(await self.scanner.get_deployments())
                }
            except Exception:
                k8s_context = {"current_namespace": self.current_namespace}

            # Process with AI assistant
            response = await self.ai_assistant.process_query(query, k8s_context)

        # Format response
        if response and "ai_response" in response:
            console.print(Panel(
                Markdown(response["ai_response"]),
                title="🤖 Groot's Response",
                border_style="green",
                box=box.ROUNDED
            ))

            # Show suggested commands
            if response.get("commands"):
                cmd_table = Table(title="Suggested Commands", border_style="cyan", box=box.ROUNDED)
                cmd_table.add_column("Command", style="cyan")
                cmd_table.add_column("Description")

                for cmd in response["commands"]:
                    cmd_table.add_row(cmd["command"], cmd["description"])

                console.print(cmd_table)

            # Show YAML examples if any
            if response.get("yaml_examples"):
                for example in response["yaml_examples"]:
                    console.print(f"\n[bold cyan]{example['title']}:[/bold cyan]")
                    console.print(Syntax(example["yaml"], "yaml", theme="monokai"))

            # Show follow-up questions
            if response.get("follow_up_questions"):
                console.print("\n[bold cyan]Follow-up questions you might want to ask:[/bold cyan]")
                for i, question in enumerate(response["follow_up_questions"]):
                    console.print(f"  {i+1}. {question}")

        return ""  # Return empty string since we printed directly

    def exit_program(self):
        """Exit the program."""
        self.running = False
        return "[green]Goodbye! I am Groot...[/green]"

    async def run(self):
        """Main loop for CLI interaction."""
        self.greet()

        try:
            while self.running:
                user_input = input(f"[{self.current_namespace}] > ")
                if user_input:
                    response = await self.process_command(user_input)
                    if response:
                        console.print(response)
        except KeyboardInterrupt:
            console.print("\n[yellow]Groot is shutting down gracefully...[/yellow]")
        finally:
            console.print("[green]Goodbye! I am Groot...[/green]")

def main():
    """Main entry point for the Groot CLI."""
    # Set up argument parser for command-line arguments
    parser = argparse.ArgumentParser(description="Groot - Kubernetes & Cloud Troubleshooting Assistant")
    parser.add_argument("--namespace", "-n", help="Set default namespace")
    parser.add_argument("--command", "-c", help="Run a single command and exit")
    parser.add_argument("--web", action="store_true", help="Start the web interface")
    parser.add_argument("--query", "-q", help="Process a natural language query and exit")
    args = parser.parse_args()

    # Start web interface if requested
    if args.web:
        from groot.web.app import start_web_app
        start_web_app()
        return

    # Run CLI
    groot = GrootCLI()

    # Set default namespace if provided
    if args.namespace:
        groot.current_namespace = args.namespace
        config.set("default_namespace", args.namespace)
        console.print(f"[green]Default namespace set to: {args.namespace}[/green]")

    # Run a single command if provided
    if args.command:
        asyncio.run(groot.process_command(args.command))
        return

    # Process a query if provided
    if args.query:
        asyncio.run(groot.process_nl_query(args.query))
        return

    # Run interactive CLI
    asyncio.run(groot.run())

if __name__ == "__main__":
    main()