"""
Command-line interface for Groot
"""

import asyncio
import sys
import os
import json
import argparse
import spacy
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
import click

from groot.k8s_scanner import K8sScanner
from groot.ai_assistant import AIAssistant
from groot.config import config

# Load NLP model for natural language understanding
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy language model...")
    spacy.cli.download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

console = Console()

class GrootCLI:
    """Enhanced Groot CLI with comprehensive Kubernetes troubleshooting capabilities."""

    def __init__(self):
        self.running = True
        self.scanner = K8sScanner()
        self.ai_assistant = AIAssistant()
        self.conversation_history = []
        self.current_namespace = config.get("default_namespace", "default")

    def greet(self):
        """Display welcome message."""
        console.print(Panel.fit(
            "[bold green]I am Groot - Advanced Kubernetes Troubleshooting Assistant[/bold green]\n\n"
            "Type [bold cyan]help[/bold cyan] to see available commands or ask me anything about your Kubernetes cluster.",
            title="🌱 Groot 🌱",
            border_style="green"
        ))

    def print_help(self):
        """Display help information."""
        help_table = Table(title="Groot Commands", border_style="cyan")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description")

        help_table.add_row("status", "Show cluster status overview")
        help_table.add_row("scan namespace [name]", "Scan resources in a namespace")
        help_table.add_row("analyze [resource] [name]", "Analyze a specific resource")
        help_table.add_row("custom-resource [type] [name]", "Analyze a custom resource")
        help_table.add_row("logs [pod] [namespace]", "Get logs for a pod")
        help_table.add_row("events [namespace]", "Get events in a namespace")
        help_table.add_row("set-namespace [name]", "Set default namespace")
        help_table.add_row("help", "Show this help message")
        help_table.add_row("exit", "Exit Groot")

        console.print(help_table)
        console.print("\nYou can also ask me natural language questions about your cluster!")

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

        elif cmd == "custom-resource" and len(parts) >= 3:
            cr_type = parts[1]
            name = parts[2]
            namespace = parts[3] if len(parts) > 3 else self.current_namespace

            return await self.analyze_custom_resource(cr_type, name, namespace)

        elif cmd == "logs" and len(parts) >= 2:
            pod = parts[1]
            namespace = parts[2] if len(parts) > 2 else self.current_namespace

            return await self.get_pod_logs(pod, namespace)

        elif cmd == "events" and len(parts) >= 1:
            namespace = parts[1] if len(parts) > 1 else self.current_namespace

            return await self.get_namespace_events(namespace)

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
        with Progress() as progress:
            task = progress.add_task("[cyan]Checking Kubernetes resource status...", total=4)

            # Get resources
            pods = await self.scanner.get_pods()
            progress.update(task, advance=1)

            deployments = await self.scanner.get_deployments()
            progress.update(task, advance=1)

            services = await self.scanner.get_services()
            progress.update(task, advance=1)

            namespaces = await self.scanner.get_namespaces()
            progress.update(task, advance=1)

        # Namespaces table
        ns_table = Table(title="📁 Namespaces", border_style="green")
        ns_table.add_column("Namespace")

        for ns in namespaces:
            ns_table.add_row(ns)

        console.print(ns_table)

        # Pods table
        pod_table = Table(title="📦 Pods", border_style="green")
        pod_table.add_column("Pod")
        pod_table.add_column("Namespace")
        pod_table.add_column("Status")

        for pod in pods:
            status = pod.status.phase
            status_style = "green" if status == "Running" else "yellow" if status == "Pending" else "red"

            pod_table.add_row(
                pod.metadata.name,
                pod.metadata.namespace,
                f"[{status_style}]{status}[/{status_style}]"
            )

        console.print(pod_table)

        # Deployments table
        deploy_table = Table(title="🚀 Deployments", border_style="green")
        deploy_table.add_column("Deployment")
        deploy_table.add_column("Replicas")
        deploy_table.add_column("Status")

        for deploy, replicas, status in deployments:
            status_style = "green" if "Healthy" in status else "red"

            deploy_table.add_row(
                deploy,
                str(replicas),
                f"[{status_style}]{status}[/{status_style}]"
            )

        console.print(deploy_table)

        # Services table
        service_table = Table(title="🔌 Services", border_style="green")
        service_table.add_column("Service")
        service_table.add_column("Type")

        for svc, svc_type in services:
            service_table.add_row(svc, svc_type)

        console.print(service_table)

        return ""  # Return empty string since we printed directly

    async def scan_namespace(self, namespace: str) -> str:
        """Scan a namespace for issues."""
        with Progress() as progress:
            task
        """Scan a namespace for issues."""
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Scanning namespace {namespace}...", total=1)

            # Analyze resources
            issues = await self.scanner.analyze_resources(namespace)
            progress.update(task, advance=1)

        if not issues:
            console.print(f"[green]✅ No issues found in namespace: {namespace}[/green]")
            return ""

        # Format issues
        console.print(f"[yellow]🔍 Issues found in namespace: {namespace}[/yellow]")

        for i, issue in enumerate(issues):
            severity = issue.get("severity", "medium")
            severity_color = "red" if severity == "high" else "yellow"

            issue_panel = Panel(
                f"[bold]Resource:[/bold] {issue['resource_type']}/{issue['name']}\n"
                f"[bold]Severity:[/bold] [{severity_color}]{severity.upper()}[/{severity_color}]\n"
                f"[bold]Issue:[/bold] {issue['issue']}\n"
                + (f"[bold]Details:[/bold] {issue['details']}\n" if "details" in issue else ""),
                title=f"Issue {i+1}",
                border_style=severity_color
            )
            console.print(issue_panel)

        # Get AI explanation
        with Progress() as progress:
            task = progress.add_task("[cyan]Getting AI analysis...", total=1)
            explanation = await self.ai_assistant.explain_issues(issues)
            progress.update(task, advance=1)

        if explanation:
            console.print(Panel(explanation, title="🤖 Groot's Analysis", border_style="green"))

        return ""  # Return empty string since we printed directly

    async def analyze_resource(self, resource_type: str, name: str, namespace: str) -> str:
        """Analyze a specific resource."""
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Analyzing {resource_type}/{name}...", total=3)

            # Get resource details
            resource_data = await self.scanner.describe_resource(resource_type, name, namespace)
            progress.update(task, advance=1)

            if "error" in resource_data:
                return f"[red]{resource_data['error']}[/red]"

            # Get related events
            field_selector = f"involvedObject.name={name}"
            events = await self.scanner.get_events(namespace, field_selector)
            progress.update(task, advance=1)

            # Prepare context for AI
            context = {
                "resource": resource_data,
                "events": events
            }

            # If it's a pod, get logs
            if resource_type == "pod":
                logs = await self.scanner.get_pod_logs(name, namespace)
                context["logs"] = logs

            # Get AI analysis
            prompt = f"Analyze this Kubernetes {resource_type} named '{name}' in namespace '{namespace}'. Identify any issues, misconfigurations, or potential improvements."
            analysis = await self.ai_assistant.get_ai_response(prompt, [], context)
            progress.update(task, advance=1)

        # Format response
        console.print(f"[green]📊 Analysis of {resource_type}/{name}:[/green]")

        # Add events summary
        if events:
            events_table = Table(title="Recent Events", border_style="yellow")
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
        console.print(Panel(analysis, title="🤖 Groot's Analysis", border_style="green"))

        return ""  # Return empty string since we printed directly

    async def analyze_custom_resource(self, cr_type: str, name: str, namespace: str) -> str:
        """Analyze a custom resource."""
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Analyzing custom resource {cr_type}/{name}...", total=2)

            # Get CR mapping
            cr_mapping = config.get("custom_resources", {})

            if cr_type.lower() not in cr_mapping:
                return f"[red]Unknown custom resource type: {cr_type}. Add it to the CR mapping in config.[/red]"

            group, version, plural = cr_mapping[cr_type.lower()]

            # Get the custom resource
            try:
                cr_data = self.scanner.custom_api.get_namespaced_custom_object(
                    group, version, namespace, plural, name
                )
                progress.update(task, advance=1)
            except Exception as e:
                return f"[red]Error getting custom resource: {e}[/red]"

            # Get AI analysis
            analysis = await self.ai_assistant.analyze_custom_resource(cr_type, cr_data)
            progress.update(task, advance=1)

        # Format response
        console.print(f"[green]📊 Analysis of {cr_type}/{name}:[/green]")

        # Add AI analysis
        console.print(Panel(analysis, title="🤖 Groot's Analysis", border_style="green"))

        return ""  # Return empty string since we printed directly

    async def get_pod_logs(self, pod_name: str, namespace: str) -> str:
        """Get logs for a specific pod."""
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Getting logs for pod {pod_name}...", total=1)
            logs = await self.scanner.get_pod_logs(pod_name, namespace)
            progress.update(task, advance=1)

        console.print(f"[green]📜 Logs for pod {pod_name}:[/green]")
        console.print(Panel(logs, border_style="blue"))

        return ""  # Return empty string since we printed directly

    async def get_namespace_events(self, namespace: str) -> str:
        """Get events for a namespace."""
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Getting events for namespace {namespace}...", total=1)
            events = await self.scanner.get_events(namespace)
            progress.update(task, advance=1)

        if not events:
            return f"[yellow]No events found in namespace {namespace}[/yellow]"

        events_table = Table(title=f"📅 Events in namespace {namespace}", border_style="green")
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

    async def process_nl_query(self, query: str) -> str:
        """Process a natural language query."""
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Processing query: {query}", total=3)

            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": query})

            # Get basic cluster info for context
            try:
                k8s_context = {
                    "current_namespace": self.current_namespace,
                    "namespaces": await self.scanner.get_namespaces(),
                    "pod_count": len(await self.scanner.get_pods()),
                    "deployment_count": len(await self.scanner.get_deployments())
                }
                progress.update(task, advance=1)
            except Exception:
                k8s_context = {"current_namespace": self.current_namespace}
                progress.update(task, advance=1)

            # Process with NLP to detect intent
            doc = nlp(query.lower())

            # Check for specific intents
            scan_namespace = False
            namespace_to_scan = self.current_namespace

            for token in doc:
                if token.text in ["scan", "check", "analyze"]:
                    scan_namespace = True
                if token.text == "namespace" and token.i < len(doc) - 1:
                    namespace_to_scan = doc[token.i + 1].text

            # If it's a scan request, get more context
            if scan_namespace:
                try:
                    issues = await self.scanner.analyze_resources(namespace_to_scan)
                    k8s_context["issues"] = issues
                except Exception:
                    pass

            progress.update(task, advance=1)

            # Get AI response
            response = await self.ai_assistant.get_ai_response(query, self.conversation_history, k8s_context)
            progress.update(task, advance=1)

            # Add to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})

            # Keep conversation history manageable
            if len(self.conversation_history) > 10:
                # Remove oldest exchanges but keep the system message
                self.conversation_history = self.conversation_history[-10:]

        return response

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
    parser = argparse.ArgumentParser(description="Groot - Kubernetes Troubleshooting Assistant")
    parser.add_argument("--namespace", "-n", help="Set default namespace")
    parser.add_argument("--command", "-c", help="Run a single command and exit")
    parser.add_argument("--web", action="store_true", help="Start the web interface")
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

    # Run interactive CLI
    asyncio.run(groot.run())

if __name__ == "__main__":
    main()