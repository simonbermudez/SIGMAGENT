"""
Multi-Agent SBDR System - Web Interface
A FastAPI web interface for the multi-agent system.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import our multi-agent system
from multiagent_sbdr_system import AgentOrchestrator
from multiagent_integrations import IntegrationManager

# Create FastAPI app
app = FastAPI(
    title="Multi-Agent SBDR System",
    description="Python-based multi-agent system for sales, account management, and customer success",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system components
orchestrator = None
integration_manager = None

# Pydantic models
class ChatMessage(BaseModel):
    session_id: str
    message: str
    user_name: Optional[str] = "Guest"
    user_email: Optional[str] = None
    customer_tier: Optional[str] = "prospect"

class ChatResponse(BaseModel):
    response: str
    agent: str
    intent: str
    confidence: float
    actions: List[str]
    user_profile: Dict[str, Any]
    metadata: Dict[str, Any]

class HealthCheck(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, bool]

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the multi-agent system on startup"""
    global orchestrator, integration_manager
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Initialize integrations
    integration_manager = IntegrationManager()
    await integration_manager.initialize_from_env()
    
    # Connect integration manager to orchestrator
    orchestrator.set_integration_manager(integration_manager)
    
    print("🚀 Multi-Agent SBDR System started successfully!")

# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    services = {}
    
    if integration_manager:
        services = await integration_manager.test_all_connections()
    
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        services=services
    )

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process a chat message through the multi-agent system"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    try:
        result = await orchestrator.process_message(
            session_id=message.session_id,
            message_content=message.message,
            user_name=message.user_name,
            user_email=message.user_email,
            customer_tier=message.customer_tier
        )
        
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# Get conversation summary
@app.get("/conversation/{session_id}")
async def get_conversation_summary(session_id: str):
    """Get conversation summary for a session"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    summary = orchestrator.get_conversation_summary(session_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return summary

# List all sessions
@app.get("/sessions")
async def list_sessions():
    """List all conversation sessions"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    sessions = []
    for session_id, profile in orchestrator.user_profiles.items():
        sessions.append({
            "session_id": session_id,
            "name": profile.name,
            "customer_tier": profile.customer_tier,
            "qualification_status": profile.qualification_status.value,
            "engagement_score": profile.engagement_score,
            "last_interaction": profile.last_interaction.isoformat() if profile.last_interaction else None
        })
    
    return {"sessions": sessions}

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message
            result = await orchestrator.process_message(
                session_id=session_id,
                message_content=message_data["message"],
                user_name=message_data.get("user_name", "Guest"),
                customer_tier=message_data.get("customer_tier", "prospect")
            )
            
            # Send response
            await websocket.send_text(json.dumps(result))
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({"error": str(e)}))

# System metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get system metrics (Prometheus format)"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Basic metrics
    total_sessions = len(orchestrator.user_profiles)
    total_messages = sum(len(history) for history in orchestrator.conversation_history.values())
    
    # Agent usage metrics
    agent_usage = {}
    for session_history in orchestrator.conversation_history.values():
        for message in session_history:
            if hasattr(message, 'sender') and 'agent' in message.sender:
                agent = message.sender.replace('_agent', '')
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
    
    # Qualification metrics
    qualification_stats = {}
    for profile in orchestrator.user_profiles.values():
        status = profile.qualification_status.value
        qualification_stats[status] = qualification_stats.get(status, 0) + 1
    
    metrics = f"""
# HELP sbdr_total_sessions Total number of conversation sessions
# TYPE sbdr_total_sessions counter
sbdr_total_sessions {total_sessions}

# HELP sbdr_total_messages Total number of messages processed
# TYPE sbdr_total_messages counter
sbdr_total_messages {total_messages}

# HELP sbdr_agent_responses_total Total responses by agent type
# TYPE sbdr_agent_responses_total counter
"""
    
    for agent, count in agent_usage.items():
        metrics += f'sbdr_agent_responses_total{{agent="{agent}"}} {count}\n'
    
    metrics += """
# HELP sbdr_qualification_status_total Total by qualification status
# TYPE sbdr_qualification_status_total gauge
"""
    
    for status, count in qualification_stats.items():
        metrics += f'sbdr_qualification_status_total{{status="{status}"}} {count}\n'
    
    return metrics

# Simple HTML interface
@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Simple HTML interface for testing"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Multi-Agent SBDR System</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .chat-container { border: 1px solid #ddd; height: 400px; overflow-y: scroll; padding: 10px; margin: 10px 0; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background-color: #e3f2fd; margin-left: 20%; }
            .agent-message { background-color: #f1f8e9; margin-right: 20%; }
            .input-container { display: flex; gap: 10px; }
            .input-container input { flex: 1; padding: 10px; }
            .input-container button { padding: 10px 20px; background-color: #2196f3; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .system-info { background-color: #fff3e0; padding: 10px; margin: 10px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🤖 Multi-Agent SBDR System</h1>
        
        <div class="system-info">
            <strong>Session ID:</strong> <span id="sessionId"></span><br>
            <strong>Current Agent:</strong> <span id="currentAgent">-</span><br>
            <strong>Qualification Status:</strong> <span id="qualificationStatus">-</span>
        </div>
        
        <div id="chatContainer" class="chat-container"></div>
        
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
        
        <script>
            const sessionId = 'web_session_' + Math.random().toString(36).substr(2, 9);
            document.getElementById('sessionId').textContent = sessionId;
            
            function addMessage(content, isUser, agentInfo) {
                const chatContainer = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (isUser ? 'user-message' : 'agent-message');
                
                if (isUser) {
                    messageDiv.textContent = content;
                } else {
                    messageDiv.innerHTML = '<strong>' + (agentInfo?.agent || 'Agent') + ':</strong> ' + content;
                    if (agentInfo) {
                        document.getElementById('currentAgent').textContent = agentInfo.agent;
                        document.getElementById('qualificationStatus').textContent = agentInfo.user_profile.qualification_status;
                    }
                }
                
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                if (!message) return;
                
                // Add user message to chat
                addMessage(message, true);
                input.value = '';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            session_id: sessionId,
                            message: message,
                            user_name: 'Web User'
                        })
                    });
                    
                    const result = await response.json();
                    addMessage(result.response, false, result);
                    
                } catch (error) {
                    addMessage('Error: ' + error.message, false);
                }
            }
            
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            // Add welcome message
            addMessage('Welcome to the Multi-Agent SBDR System! How can I help you today?', false, {agent: 'SBDR Agent'});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)