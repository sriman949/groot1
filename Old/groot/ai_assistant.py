# groot/ai_assistant.py
import json
import asyncio
import os
from typing import List, Dict, Any, Optional, Tuple
import openai
from rich.console import Console
from groot.config import config
from groot.nlp_engine import NLPEngine
from groot.knowledge_base import KnowledgeBase
from groot.command_generator import CommandGenerator

console = Console()

class AIAssistant:
    """Enhanced AI assistant for Kubernetes and cloud troubleshooting."""

    def __init__(self, api_key: str = None):
        """Initialize the AI assistant."""
        # Use API key from config or parameter
        self.api_key = api_key or config.get("openai_api_key")
        if not self.api_key:
            console.print("[yellow]Warning: No OpenAI API key provided. AI features will be limited.[/yellow]")
        else:
            openai.api_key = self.api_key

        # Initialize components
        self.nlp_engine = NLPEngine()
        self.knowledge_base = KnowledgeBase()
        self.command_generator = CommandGenerator()

        # Conversation memory
        self.conversation_history = []
        self.context = {}

    async def process_query(self, query: str, k8s_context: Dict = None) -> Dict[str, Any]:
        """Process a natural language query and return a comprehensive response."""
        # Parse the query
        parsed_query = self.nlp_engine.parse_query(query)

        # Update context with K8s information
        if k8s_context:
            self.context.update(k8s_context)

        # Search knowledge base for relevant information
        kb_results = self.knowledge_base.search(parsed_query)

        # Generate relevant commands
        commands = self.command_generator.generate_commands(parsed_query, self.context)

        # Generate YAML examples if needed
        yaml_examples = []
        if parsed_query["context"]["requires_code"]:
            yaml_examples = self.command_generator.generate_yaml_examples(parsed_query)

        # Generate follow-up questions
        follow_ups = self.nlp_engine.generate_follow_up_questions(parsed_query, self.context)

        # Prepare the response
        response = {
            "original_query": query,
            "parsed_query": parsed_query,
            "knowledge_base_results": kb_results,
            "commands": commands,
            "yaml_examples": yaml_examples,
            "follow_up_questions": follow_ups,
            "ai_response": await self._generate_ai_response(query, parsed_query, kb_results, commands, yaml_examples)
        }

        # Update conversation history
        self._update_conversation_history(query, response["ai_response"])

        return response

    async def _generate_ai_response(self, query: str, parsed_query: Dict, kb_results: List[Dict],
                                    commands: List[Dict], yaml_examples: List[Dict]) -> str:
        """Generate an AI response using OpenAI."""
        if not self.api_key:
            return "AI features are disabled. Please set OPENAI_API_KEY environment variable or configure it in ~/.groot/config.yaml."

        try:
            # Prepare messages with conversation history
            messages = self.conversation_history.copy()

            # Add system message with Kubernetes expertise
            system_message = {
                "role": "system",
                "content": """You are Groot, an AI assistant specialized in Kubernetes and cloud infrastructure troubleshooting.
                You have deep knowledge of Kubernetes concepts, resources, controllers, operators, cloud providers (AWS, GCP, Azure),
                and best practices. Your goal is to help engineers solve problems with their Kubernetes clusters and cloud infrastructure.
                Be specific, concise, and provide actionable recommendations. Focus on practical solutions and explain concepts clearly.
                When providing commands or code, explain what they do and why they're useful."""
            }

            messages.insert(0, system_message)

            # Add knowledge base results as context
            if kb_results:
                kb_context = "Here is relevant information from my knowledge base:\n\n"
                for i, result in enumerate(kb_results):
                    kb_context += f"--- {result.get('title', 'Information')} ---\n"
                    if 'description' in result:
                        kb_context += f"{result['description']}\n"
                    if 'symptoms' in result:
                        kb_context += "Symptoms:\n" + "\n".join([f"- {s}" for s in result['symptoms']]) + "\n"
                    if 'causes' in result:
                        kb_context += "Possible causes:\n" + "\n".join([f"- {c}" for c in result['causes']]) + "\n"
                    if 'solutions' in result:
                        kb_context += "Solutions:\n" + "\n".join([f"- {s}" for s in result['solutions']]) + "\n"
                    if 'content' in result:
                        kb_context += f"{result['content']}\n"
                    kb_context += "\n"

                messages.append({"role": "system", "content": kb_context})

            # Add commands as context
            if commands:
                cmd_context = "Here are relevant commands that might help:\n\n"
                for cmd in commands:
                    cmd_context += f"Command: {cmd['command']}\n"
                    cmd_context += f"Purpose: {cmd['description']}\n\n"

                messages.append({"role": "system", "content": cmd_context})

            # Add YAML examples as context
            if yaml_examples:
                yaml_context = "Here are relevant YAML examples:\n\n"
                for example in yaml_examples:
                    yaml_context += f"--- {example['title']} ---\n"
                    yaml_context += f"```yaml\n{example['yaml']}\n```\n\n"

                messages.append({"role": "system", "content": yaml_context})

            # Add parsed query information
            query_info = f"""
            The user's query has been parsed as follows:
            - Intent: {parsed_query['intent']['action']}
            - Resource types: {', '.join(parsed_query['entities']['resource_type']) if parsed_query['entities']['resource_type'] else 'Not specified'}
            - Resource names: {', '.join(parsed_query['entities']['resource_name']) if parsed_query['entities']['resource_name'] else 'Not specified'}
            - Namespace: {parsed_query['entities']['namespace'] or 'Not specified'}
            - Issue types: {', '.join(parsed_query['entities']['issue_type']) if parsed_query['entities']['issue_type'] else 'Not specified'}
            - Cloud providers: {', '.join(parsed_query['entities']['cloud_provider']) if parsed_query['entities']['cloud_provider'] else 'Not specified'}
            
            The user {'' if parsed_query['context']['requires_code'] else 'does not '}needs code examples.
            The user {'' if parsed_query['context']['requires_explanation'] else 'does not '}needs detailed explanations.
            """

            messages.append({"role": "system", "content": query_info})

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

    def _update_conversation_history(self, query: str, response: str):
        """Update the conversation history with the latest exchange."""
        # Add the current exchange
        self.conversation_history.append({"role": "user", "content": query})
        self.conversation_history.append({"role": "assistant", "content": response})

        # Keep conversation history manageable (last 10 exchanges)
        if len(self.conversation_history) > 20:  # 10 exchanges (user + assistant)
            # Remove oldest exchanges but keep the system message if present
            if self.conversation_history[0]["role"] == "system":
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-19:]
            else:
                self.conversation_history = self.conversation_history[-20:]

    async def explain_k8s_concept(self, concept: str) -> str:
        """Explain a Kubernetes concept in simple terms."""
        if not self.api_key:
            return "AI explanation is disabled. Please set OPENAI_API_KEY environment variable or configure it in ~/.groot/config.yaml."

        try:
            # Prepare the prompt
            prompt = f"""Explain the Kubernetes concept "{concept}" in simple terms. 
            Include what it is, why it's important, and how it works. 
            Provide a simple example if applicable."""

            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Groot, an AI assistant specialized in Kubernetes. Explain concepts clearly and concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            console.print(f"[red]Error explaining concept: {e}[/red]")
            return f"Error explaining concept: {e}"

    async def compare_resources(self, resource1: str, resource2: str) -> str:
        """Compare two Kubernetes resources and explain the differences."""
        if not self.api_key:
            return "AI comparison is disabled. Please set OPENAI_API_KEY environment variable or configure it in ~/.groot/config.yaml."

        try:
            # Prepare the prompt
            prompt = f"""Compare the Kubernetes resources "{resource1}" and "{resource2}".
            Explain:
            1. The purpose of each resource
            2. Key differences in functionality
            3. When to use one over the other
            4. How they interact with each other (if applicable)
            """

            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are Groot, an AI assistant specialized in Kubernetes. Provide clear, accurate comparisons."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            return response.choices[0].message.content

        except Exception as e:
            console.print(f"[red]Error comparing resources: {e}[/red]")
            return f"Error comparing resources: {e}"

    async def suggest_best_practices(self, resource_type: str) -> List[Dict]:
        """Suggest best practices for a specific resource type."""
        # Search knowledge base for best practices
        query = {
            "entities": {
                "resource_type": [resource_type]
            }
        }

        best_practices = self.knowledge_base.search(query)

        # Filter for best practice entries
        return [bp for bp in best_practices if "best-practice" in bp.get("tags", [])]