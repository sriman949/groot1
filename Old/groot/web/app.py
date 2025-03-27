"""
Web interface for Groot
"""

import asyncio
import threading
from flask import Flask, render_template, request, jsonify
from groot.k8s_scanner import K8sScanner
from groot.ai_assistant import AIAssistant
from groot.config import config

app = Flask(__name__)
scanner = K8sScanner()
ai_assistant = AIAssistant()
conversation_history = []

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page."""
    return render_template('dashboard.html')

@app.route('/analysis')
def analysis():
    """Render the analysis page."""
    return render_template('analysis.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get cluster status."""
    try:
        # Run async function in a separate thread
        loop = asyncio.new_event_loop()

        async def get_data():
            namespaces = await scanner.get_namespaces()
            pods = await scanner.get_pods()
            deployments = await scanner.get_deployments()
            services = await scanner.get_services()

            return {
                "namespaces": namespaces,
                "pods": [
                    {
                        "name": pod.metadata.name,
                        "namespace": pod.metadata.namespace,
                        "status": pod.status.phase
                    } for pod in pods
                ],
                "deployments": [
                    {
                        "name": name,
                        "replicas": replicas,
                        "status": status
                    } for name, replicas, status in deployments
                ],
                "services": [
                    {
                        "name": name,
                        "type": type
                    } for name, type in services
                ]
            }

        result = asyncio.run(get_data())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def scan_namespace():
    """Scan a namespace for issues."""
    data = request.json
    namespace = data.get('namespace', 'default')

    try:
        # Run async function in a separate thread
        loop = asyncio.new_event_loop()

        async def scan():
            issues = await scanner.analyze_resources(namespace)

            if issues:
                explanation = await ai_assistant.explain_issues(issues)
                return {
                    "issues": issues,
                    "explanation": explanation
                }
            else:
                return {
                    "issues": [],
                    "explanation": "No issues found."
                }

        result = asyncio.run(scan())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_resource():
    """Analyze a specific resource."""
    data = request.json
    resource_type = data.get('type')
    name = data.get('name')
    namespace = data.get('namespace', 'default')

    if not resource_type or not name:
        return jsonify({"error": "Resource type and name are required"}), 400

    try:
        # Run async function in a separate thread
        loop = asyncio.new_event_loop()

        async def analyze():
            # Get resource details
            resource_data = await scanner.describe_resource(resource_type, name, namespace)

            if "error" in resource_data:
                return {"error": resource_data["error"]}

            # Get related events
            field_selector = f"involvedObject.name={name}"
            events = await scanner.get_events(namespace, field_selector)

            # Prepare context for AI
            context = {
                "resource": resource_data,
                "events": events
            }

            # If it's a pod, get logs
            if resource_type == "pod":
                logs = await scanner.get_pod_logs(name, namespace)
                context["logs"] = logs

            # Get AI analysis
            prompt = f"Analyze this Kubernetes {resource_type} named '{name}' in namespace '{namespace}'. Identify any issues, misconfigurations, or potential improvements."
            analysis = await ai_assistant.get_ai_response(prompt, [], context)

            return {
                "resource": resource_data,
                "events": events[:5],  # Only return the 5 most recent events
                "logs": logs if resource_type == "pod" else None,
                "analysis": analysis
            }

        result = asyncio.run(analyze())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a chat message."""
    global conversation_history

    data = request.json
    message = data.get('message')

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # Run async function in a separate thread
        loop = asyncio.new_event_loop()

        async def process_message():
            # Add to conversation history
            conversation_history.append({"role": "user", "content": message})

            # Get basic cluster info for context
            try:
                k8s_context = {
                    "current_namespace": config.get("default_namespace", "default"),
                    "namespaces": await scanner.get_namespaces(),
                    "pod_count": len(await scanner.get_pods()),
                    "deployment_count": len(await scanner.get_deployments())
                }
            except Exception:
                k8s_context = {"current_namespace": config.get("default_namespace", "default")}

            # Get AI response
            response = await ai_assistant.get_ai_response(message, conversation_history, k8s_context)

            # Add to conversation history
            conversation_history.append({"role": "assistant", "content": response})

            # Keep conversation history manageable
            if len(conversation_history) > 10:
                # Remove oldest exchanges but keep the system message
                conversation_history = conversation_history[-10:]

            return {"response": response}

        result = asyncio.run(process_message())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def start_web_app():
    """Start the web application."""
    host = config.get("web", {}).get("host", "127.0.0.1")
    port = config.get("web", {}).get("port", 8080)
    debug = config.get("web", {}).get("debug", False)

    print(f"Starting Groot web interface at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    start_web_app()