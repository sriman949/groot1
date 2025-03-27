# Groot: Advanced Kubernetes Troubleshooting Assistant

Groot is an AI-powered CLI tool designed to help DevOps engineers and SREs troubleshoot Kubernetes clusters. It combines deep Kubernetes knowledge with advanced AI capabilities to identify issues, suggest fixes, and provide context-aware recommendations.

## Features

- **Comprehensive Kubernetes Analysis**: Scan namespaces, deployments, services, and other resources for issues
- **Custom Resource Support**: Analyze custom controllers and operators with context-specific knowledge
- **Natural Language Interface**: Ask questions in plain English like "why are my pods crashing in production?"
- **AI-Powered Recommendations**: Get intelligent, actionable recommendations for fixing issues
- **Conversation History**: Maintain context across multiple queries for more relevant responses
- **Rich Output Formatting**: Clear, color-coded tables and structured output for better readability

## Installation

### Using pip

```bash
pip install groot-k8s-cli

# Groot CLI - AI-Powered Kubernetes & Cloud Troubleshooting Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/yourusername/groot-cli/main/docs/images/groot-logo.png" alt="Groot Logo" width="200"/>
</p>

<p align="center">
  <em>I am Groot! Your AI-powered sidekick for Kubernetes and cloud infrastructure troubleshooting.</em>
</p>

## Overview

Groot is an intelligent CLI tool that helps engineers troubleshoot and resolve issues with Kubernetes clusters and cloud infrastructure. Using natural language processing and AI, Groot understands your questions, analyzes your cluster, and provides actionable recommendations.

## Features

- 🤖 **Natural Language Interface**: Ask questions in plain English
- 🔍 **Intelligent Analysis**: Automatically detects and diagnoses common Kubernetes issues
- 📊 **Resource Visualization**: Get clear insights into your cluster's health
- 📚 **Knowledge Base**: Access best practices and solutions for common problems
- 🛠️ **Command Generation**: Get suggested kubectl commands to fix issues
- ☁️ **Multi-Cloud Support**: Works with AWS, GCP, and Azure

## Installation

### Prerequisites

- Python 3.8+
- kubectl configured with access to your cluster
- OpenAI API key (for AI features)

### Install via pip

```bash
pip install groot-cli

### Manual Installation
git clone https://github.com/yourusername/groot-cli.git
cd groot-cli
pip install -e .

### Configuration

Create a configuration file at `~/.groot/config.yaml`:

```yaml

```
# OpenAI API key for AI features
openai_api_key: "your-api-key-here"

# Default namespace
default_namespace: "default"

# Logging level (debug, info, warning, error)
log_level: "info"


## Quick Start

```shellscript

```
# Start Groot CLI
groot

# Start with a specific namespace
groot --namespace production

# Ask a question directly
groot --query "Why are my pods crashing in the production namespace?"

# Run a specific command
groot --command "analyze deployment my-app"

# Start the web interface
groot --web


Thought for 3 seconds### README Files for Groot CLI

I'll create two comprehensive README files for Groot CLI - one for users and one for developers.

## 1. User README (README.md)

```markdown
# Groot CLI - AI-Powered Kubernetes & Cloud Troubleshooting Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/yourusername/groot-cli/main/docs/images/groot-logo.png" alt="Groot Logo" width="200"/>
</p>

<p align="center">
  <em>I am Groot! Your AI-powered sidekick for Kubernetes and cloud infrastructure troubleshooting.</em>
</p>

## Overview

Groot is an intelligent CLI tool that helps engineers troubleshoot and resolve issues with Kubernetes clusters and cloud infrastructure. Using natural language processing and AI, Groot understands your questions, analyzes your cluster, and provides actionable recommendations.

## Features

- 🤖 **Natural Language Interface**: Ask questions in plain English
- 🔍 **Intelligent Analysis**: Automatically detects and diagnoses common Kubernetes issues
- 📊 **Resource Visualization**: Get clear insights into your cluster's health
- 📚 **Knowledge Base**: Access best practices and solutions for common problems
- 🛠️ **Command Generation**: Get suggested kubectl commands to fix issues
- ☁️ **Multi-Cloud Support**: Works with AWS, GCP, and Azure

## Installation

### Prerequisites

- Python 3.8+
- kubectl configured with access to your cluster
- OpenAI API key (for AI features)

### Install via pip

```bash
pip install groot-cli
```

### Manual Installation

```shellscript
git clone https://github.com/yourusername/groot-cli.git
cd groot-cli
pip install -e .
```

### Configuration

Create a configuration file at `~/.groot/config.yaml`:

```yaml
# OpenAI API key for AI features
openai_api_key: "your-api-key-here"

# Default namespace
default_namespace: "default"

# Logging level (debug, info, warning, error)
log_level: "info"
```

## Quick Start

```shellscript
# Start Groot CLI
groot

# Start with a specific namespace
groot --namespace production

# Ask a question directly
groot --query "Why are my pods crashing in the production namespace?"

# Run a specific command
groot --command "analyze deployment my-app"

# Start the web interface
groot --web
```

## Usage

### Interactive Mode

Start Groot in interactive mode:

```shellscript
groot
```

You'll see a welcome message and a prompt where you can enter commands or natural language questions:

```plaintext
🌱 Groot 🌱
│ I am Groot - Advanced Kubernetes & Cloud Troubleshooting Assistant │
│                                                                    │
│ Type help to see available commands or ask me anything about your  │
│ Kubernetes cluster or cloud infrastructure.                        │
└────────────────────────────────────────────────────────────────────┘

[default] > 
```

### Commands

Here are some of the most useful commands:

| Command | Description
|-----|-----
| `status` | Show cluster status overview
| `scan namespace [name]` | Scan resources in a namespace
| `analyze [resource] [name]` | Analyze a specific resource
| `logs [pod] [namespace]` | Get logs for a pod
| `events [namespace]` | Get events in a namespace
| `explain [concept]` | Explain a Kubernetes concept
| `compare [resource1] [resource2]` | Compare two Kubernetes resources
| `best-practices [resource]` | Show best practices for a resource
| `set-namespace [name]` | Set default namespace
| `help` | Show help message
| `exit` | Exit Groot


### Natural Language Queries

You can ask Groot questions in natural language:

```plaintext
[default] > Why are my pods crashing in the production namespace?
```

```plaintext
[default] > How do I troubleshoot network connectivity issues between services?
```

```plaintext
[default] > What's the difference between a Deployment and a StatefulSet?
```

```plaintext
[default] > Show me how to set up an Ingress with TLS
```

## Examples

### Analyzing a Deployment

```plaintext
[default] > analyze deployment nginx
```

Groot will analyze the deployment and provide:

- Recent events
- Configuration review
- Potential issues
- Recommendations
- Suggested commands


### Troubleshooting Pod Crashes

```plaintext
[default] > Why are my pods crashing in the production namespace?
```

Groot will:

1. Scan the production namespace
2. Identify pods with issues
3. Analyze logs and events
4. Provide potential causes
5. Suggest solutions
6. Generate helpful kubectl commands


### Explaining Kubernetes Concepts

```plaintext
[default] > explain pod disruption budget
```

Groot will provide a clear explanation of the concept, its purpose, and examples of how to use it.

## Troubleshooting

### API Key Issues

If you see errors about the OpenAI API key:

1. Make sure you've set your API key in `~/.groot/config.yaml`
2. Check that your API key is valid and has sufficient credits


### Kubernetes Connection Issues

If Groot can't connect to your cluster:

1. Verify that kubectl is working: `kubectl get nodes`
2. Check your kubeconfig file: `kubectl config view`
3. Ensure you have the necessary permissions


### Other Issues

For more help, please:

1. Check the [FAQ](https://github.com/yourusername/groot-cli/wiki/FAQ)
2. Open an issue on [GitHub](https://github.com/yourusername/groot-cli/issues)


## License

MIT License

```plaintext

## 2. Developer README (CONTRIBUTING.md)

```markdown
# Contributing to Groot CLI

Thank you for your interest in contributing to Groot CLI! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Project Architecture](#project-architecture)
- [Development Setup](#development-setup)
- [Code Organization](#code-organization)
- [Testing](#testing)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style](#code-style)

## Project Architecture

Groot CLI is built with a modular architecture:

```

┌─────────────────┐
│     CLI App     │
└────────┬────────┘
│
▼
┌─────────────┬─────────────────────┬─────────────┐
│  NLP Engine │  Kubernetes Scanner │ AI Assistant │
└──────┬──────┴──────────┬──────────┴──────┬──────┘
│                 │                 │
▼                 ▼                 ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Knowledge   │  │ Kubernetes  │  │ Command     │
│ Base        │  │ API Client  │  │ Generator   │
└─────────────┘  └─────────────┘  └─────────────┘

```plaintext

- **CLI App**: The main entry point and user interface
- **NLP Engine**: Processes natural language queries
- **Kubernetes Scanner**: Interacts with Kubernetes API
- **AI Assistant**: Generates intelligent responses
- **Knowledge Base**: Stores information about common issues
- **Command Generator**: Creates kubectl and cloud CLI commands

## Development Setup

### Prerequisites

- Python 3.8+
- kubectl
- OpenAI API key (for AI features)
- Git

### Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/groot-cli.git
   cd groot-cli
```

3. Create a virtual environment:

```shellscript
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


4. Install development dependencies:

```shellscript
pip install -e ".[dev]"
```


5. Create a development config file:

```shellscript
mkdir -p ~/.groot
cp config.example.yaml ~/.groot/config.yaml
# Edit ~/.groot/config.yaml with your settings
```




### Running in Development Mode

```shellscript
# Run the CLI directly from source
python -m groot.cli

# Run with specific arguments
python -m groot.cli --namespace default
```

## Code Organization

The project is organized into the following modules:

```plaintext
groot/
├── __init__.py
├── cli.py                # Main CLI interface
├── config.py             # Configuration management
├── k8s_scanner.py        # Kubernetes API interaction
├── ai_assistant.py       # AI-powered assistance
├── nlp_engine.py         # Natural language processing
├── knowledge_base.py     # Knowledge base management
├── command_generator.py  # Command generation
├── web/                  # Web interface (optional)
│   ├── __init__.py
│   ├── app.py
│   └── templates/
└── utils/                # Utility functions
    ├── __init__.py
    └── helpers.py
```

### Key Components

- **cli.py**: The main CLI interface that handles user input and displays results
- **k8s_scanner.py**: Interacts with the Kubernetes API to get cluster information
- **ai_assistant.py**: Processes queries and generates responses using AI
- **nlp_engine.py**: Parses natural language queries to extract intent and entities
- **knowledge_base.py**: Manages the knowledge base of common issues and solutions
- **command_generator.py**: Generates kubectl and cloud CLI commands


## Testing

We use pytest for testing. To run the tests:

```shellscript
# Run all tests
pytest

# Run specific test file
pytest tests/test_nlp_engine.py

# Run with coverage
pytest --cov=groot
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with the `test_` prefix
- Use meaningful test names that describe what is being tested
- Mock external dependencies (Kubernetes API, OpenAI API)


Example test:

```python
# tests/test_nlp_engine.py
from groot.nlp_engine import NLPEngine

def test_parse_query_extracts_resource_type():
    engine = NLPEngine()
    result = engine.parse_query("Why are my pods crashing?")
    assert "pod" in result["entities"]["resource_type"]
```

## Contribution Guidelines

### Types of Contributions

We welcome the following types of contributions:

- Bug fixes
- Feature additions
- Documentation improvements
- Test coverage improvements
- Code refactoring


### Before Contributing

1. Check the [Issues](https://github.com/yourusername/groot-cli/issues) to see if your contribution is already being discussed
2. For major changes, open an issue first to discuss your proposed changes


## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add or update tests as necessary
5. Update documentation as necessary
6. Run the tests to ensure they pass
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request against the `main` branch


### Pull Request Template

When creating a pull request, please include:

- A clear description of the changes
- Any related issues (e.g., "Fixes #123")
- Screenshots or examples if applicable
- Confirmation that tests pass


## Code Style

We follow PEP 8 with some modifications:

- Line length: 100 characters
- Use 4 spaces for indentation
- Use docstrings for all public methods and classes
- Type hints are encouraged


We use the following tools to enforce code style:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For linting
- **mypy**: For type checking


To check your code style:

```shellscript
# Format code
black groot tests

# Sort imports
isort groot tests

# Lint
flake8 groot tests

# Type check
mypy groot
```

## Documentation

We use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description of the function.
    
    Longer description explaining the function in detail.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When something goes wrong
    """
    # Function implementation
```