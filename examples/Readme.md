##  `README.md`

```markdown
# Groot CLI

An AI-powered CLI for Kubernetes troubleshooting and management.

## Features

- Natural language interface for Kubernetes operations
- Intelligent troubleshooting of cluster issues
- Automated analysis of deployments, services, and other resources
- Web interface for visual interaction with your cluster
- AI-powered recommendations for best practices

## Installation

### From PyPI

```bash
pip install groot-cli
```

### From Source

```shellscript
git clone https://github.com/groot-ai/groot.git
cd groot
pip install -e .
```

## Configuration

Create a `.groot.yaml` file in your home directory:

```yaml
# Kubernetes configuration
kubernetes:
  context: default  # or specify your context
  namespace: default  # default namespace

# OpenAI configuration
openai:
  api_key: your_openai_api_key  # or set OPENAI_API_KEY environment variable

# Web interface configuration
web:
  enabled: true
  host: 127.0.0.1
  port: 8000
```

Or use environment variables:

```shellscript
export OPENAI_API_KEY=your_openai_api_key
export GROOT_K8S_CONTEXT=your_k8s_context
export GROOT_K8S_NAMESPACE=your_namespace
```

## Usage

### CLI Commands

```shellscript
# Get help
groot --help

# Ask Groot a question
groot "Why are my pods crashing in production?"

# Analyze a deployment
groot analyze deployment nginx

# Get recommendations for a service
groot recommend service frontend

# Start the web interface
groot web start
```

### Web Interface

Access the web interface at `http://localhost:8000` after starting it with `groot web start`.


## 5. `.groot.yaml` (Example Configuration)

```yaml
# Kubernetes configuration
kubernetes:
  context: default  # or specify your context
  namespace: default  # default namespace
  kubeconfig: ~/.kube/config  # path to kubeconfig file

# OpenAI configuration
openai:
  api_key: ""  # Set your OpenAI API key here or use environment variable
  model: "gpt-4o"  # OpenAI model to use

# Web interface configuration
web:
  enabled: true
  host: 127.0.0.1
  port: 8000
  debug: false

# Logging configuration
logging:
  level: info  # debug, info, warning, error
  file: ~/.groot/groot.log  # log file path

# Analysis configuration
analysis:
  max_events: 50  # maximum number of events to analyze
  max_logs: 100  # maximum number of log lines to analyze
  timeout: 30  # timeout in seconds for analysis operations

# Knowledge base configuration
knowledge_base:
  local_path: ~/.groot/knowledge  # path to local knowledge base
  update_interval: 86400  # update interval in seconds (1 day)
