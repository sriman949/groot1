"""
AI assistant module for Groot
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
import openai
from rich.console import Console
from groot.config import config

console = Console()

class AIAssistant:
    """Enhanced AI assistant for Kubernetes troubleshooting."""

    def __init__(self, api_key: str = None):
        # Use API key from config or parameter
        self.api_key = api_key or config.get("openai_api_key")
        if not self.api_key:
            console.print("[yellow]Warning: No OpenAI API key provided. AI features will be limited.[/yellow]")
        else:
            openai.api_key = self.api_key

    async def get_ai_response(self, query: str, conversation_history: List[Dict], k8s_context: Dict = None) -> str:
        """Get AI response for a user query with Kubernetes context."""
        if not self.api_key:
            return "AI features are disabled. Please set OPENAI_API_KEY environment variable or configure it in ~/.groot/config.yaml."

        try:
            # Prepare messages with conversation history
            messages = conversation_history.copy()

            # Add system message with Kubernetes expertise
            system_message = {
                "role": "system",
                "content": """You are Groot, an AI assistant specialized in Kubernetes troubleshooting.
                You have deep knowledge of Kubernetes concepts, resources, controllers, operators,
                and best practices. Analyze the provided Kubernetes resources and identify issues,
                misconfigurations, or potential improvements. Be specific and provide actionable
                recommendations. Focus on security, performance, reliability, and scalability."""
            }

            messages.insert(0, system_message)

            # Add Kubernetes context if available
            if k8s_context:
                context_message = {
                    "role": "system",
                    "content": f"Here is the current Kubernetes context:\n{json.dumps(k8s_context, indent=2)}"
                }
                messages.append(context_message)

            # Add the current query
            messages.append({"role": "user", "content": query})

            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            console.print(f"[red]Error getting AI response: {e}[/red]")
            return f"Error getting AI response: {e}"

    async def explain_issues(self, issues: List[Dict]) -> str:
        """Explain Kubernetes issues and provide recommendations."""
        if not self.api_key:
            return "AI explanation is disabled. Please set OPENAI_API_KEY environment variable or configure it in ~/.groot/config.yaml."

        try:
            # Prepare the prompt with issues
            issues_json = json.dumps(issues, indent=2)

            prompt = f"""Analyze the following Kubernetes issues and provide:
            1. A clear explanation of each issue
            2. Likely root causes
            3. Specific recommendations to fix each issue
            4. Best practices to prevent similar issues in the future
            
            Issues:
            {issues_json}
            
            Format your response with clear sections for each issue.
            """

            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Groot, an AI assistant specialized in Kubernetes troubleshooting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            console.print(f"[red]Error explaining issues: {e}[/red]")
            return f"Error explaining issues: {e}"

    async def analyze_custom_resource(self, resource_type: str, resource_data: Dict) -> str:
        """Analyze a custom resource and provide insights."""
        if not self.api_key:
            return "AI analysis is disabled. Please set OPENAI_API_KEY environment variable or configure it in ~/.groot/config.yaml."

        try:
            # Prepare the prompt with resource data
            resource_json = json.dumps(resource_data, indent=2)

            prompt = f"""Analyze the following Kubernetes custom resource of type {resource_type}:
            
            {resource_json}
            
            Provide:
            1. An overview of what this resource does
            2. Any issues or misconfigurations
            3. Best practices and recommendations
            4. Potential security concerns
            """

            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Groot, an AI assistant specialized in Kubernetes troubleshooting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return response.choices[0].message.content

        except Exception as e:
            console.print(f"[red]Error analyzing custom resource: {e}[/red]")
            return f"Error analyzing custom resource: {e}"