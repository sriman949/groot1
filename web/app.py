"""Web interface for Groot CLI."""

import asyncio
import json
from typing import Dict, Any, List
import os
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from groot.ai_assistant import AIAssistant
from groot.k8s_scanner import K8sScanner
from groot.config import config

# Initialize FastAPI app
app = FastAPI(title="Groot Web Interface")

# Set up templates and static files
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

templates = Jinja2Templates(directory=str(templates_dir))
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Initialize components
ai_assistant = AIAssistant()
k8s_scanner = K8sScanner()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Models
class Query(BaseModel):
    query: str
    namespace: str = "default"

# Routes
@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    """Render the home page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/status", response_class=HTMLResponse)
async def get_status(request: Request):
    """Render the cluster status page."""
    return templates.TemplateResponse("status.html", {"request": request})

@app.get("/api/namespaces")
async def get_namespaces():
    """Get all namespaces in the cluster."""
    try:
        namespaces = await k8s_scanner.get_namespaces()
        return {"namespaces": namespaces}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/status")
async def get_cluster_status():
    """Get cluster status information."""
    try:
        pods = await k8s_scanner.get_pods()
        deployments = await k8s_scanner.get_deployments()
        services = await k8s_scanner.get_services()

        # Count pod statuses
        pod_status_counts = {}
        for pod in pods:
            status = pod.status.phase
            pod_status_counts[status] = pod_status_counts.get(status, 0) + 1

        return {
            "pod_count": len(pods),
            "deployment_count": len(deployments),
            "service_count": len(services),
            "pod_statuses": pod_status_counts
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/query")
async def process_query(query: Query):
    """Process a natural language query."""
    try:
        # Get basic cluster info for context
        try:
            k8s_context = {
                "current_namespace": query.namespace,
                "namespaces": await k8s_scanner.get_namespaces(),
                "pod_count": len(await k8s_scanner.get_pods()),
                "deployment_count": len(await k8s_scanner.get_deployments())
            }
        except Exception:
            k8s_context = {"current_namespace": query.namespace}

        # Process with AI assistant
        response = await ai_assistant.process_query(query.query, k8s_context)

        return response
    except Exception as e:
        return {"error": str(e)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)

            if data_json.get("type") == "query":
                # Process query
                query = data_json.get("query", "")
                namespace = data_json.get("namespace", "default")

                # Get basic cluster info for context
                try:
                    k8s_context = {
                        "current_namespace": namespace,
                        "namespaces": await k8s_scanner.get_namespaces(),
                        "pod_count": len(await k8s_scanner.get_pods()),
                        "deployment_count": len(await k8s_scanner.get_deployments())
                    }
                except Exception:
                    k8s_context = {"current_namespace": namespace}

                # Process with AI assistant
                response = await ai_assistant.process_query(query, k8s_context)

                # Send response
                await manager.send_message(json.dumps({
                    "type": "response",
                    "response": response
                }), websocket)

            elif data_json.get("type") == "status_update":
                # Get cluster status
                try:
                    pods = await k8s_scanner.get_pods()
                    deployments = await k8s_scanner.get_deployments()
                    services = await k8s_scanner.get_services()

                    # Count pod statuses
                    pod_status_counts = {}
                    for pod in pods:
                        status = pod.status.phase
                        pod_status_counts[status] = pod_status_counts.get(status, 0) + 1

                    status_data = {
                        "pod_count": len(pods),
                        "deployment_count": len(deployments),
                        "service_count": len(services),
                        "pod_statuses": pod_status_counts
                    }

                    # Send status update
                    await manager.send_message(json.dumps({
                        "type": "status_update",
                        "status": status_data
                    }), websocket)
                except Exception as e:
                    await manager.send_message(json.dumps({
                        "type": "error",
                        "error": str(e)
                    }), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

def start_web_app(host: str = "0.0.0.0", port: int = 8000):
    """Start the web application."""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_web_app()