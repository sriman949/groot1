#!/usr/bin/env python3
"""
Example usage of the Groot CLI programmatically.
"""

import os
import sys
from groot.ai_assistant import AIAssistant
from groot.k8s_scanner import KubernetesScanner
from groot.config import Config

def main():
    # Load configuration
    config = Config()
    config.load_from_file("~/.groot.yaml")

    # Override with environment variables if set
    if "OPENAI_API_KEY" in os.environ:
        config.openai.api_key = os.environ["OPENAI_API_KEY"]

    # Initialize components
    scanner = KubernetesScanner(config)
    assistant = AIAssistant(config)

    # Scan the cluster
    print("Scanning Kubernetes cluster...")
    cluster_info = scanner.scan_cluster()

    # Ask a question
    question = "Why are my pods crashing in production?"
    print(f"\nQuestion: {question}")

    # Get AI response
    response = assistant.ask(question, context=cluster_info)
    print(f"\nGroot's Response:\n{response.ai_response}")

    # Show suggested commands
    if response.commands:
        print("\nSuggested Commands:")
        for cmd in response.commands:
            print(f"- {cmd.command}: {cmd.description}")

    # Show follow-up questions
    if response.follow_up_questions:
        print("\nFollow-up Questions:")
        for q in response.follow_up_questions:
            print(f"- {q}")

if __name__ == "__main__":
    main()