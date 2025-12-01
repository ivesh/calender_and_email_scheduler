"""
Enterprise Gen AI Multi-Agent Application
==========================================

Unified FastAPI application integrating:
- Jarvis ADK: Calendar management, trip planning, email
- Lenny Lang: Language translation, weather information
- Taylor Crew: Multi-agent trip planning and email automation
- MCP: Model Context Protocol tools
- A2A: Agent-to-agent communication

Author: Enterprise Agents Team
Version: 1.0.0
"""

import asyncio
import base64
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import AsyncIterable, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

# Import agents from different frameworks
from app.jarvis_adk.agent import root_agent as jarvis_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Application metadata
APP_NAME = "Enterprise Gen AI Multi-Agent System"
APP_VERSION = "1.0.0"
session_service = InMemorySessionService()

# Initialize FastAPI app
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Unified multi-framework agent system with ADK, LangChain, and CrewAI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
STATIC_DIR = Path(__file__).parent / "app" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ============================================================================
# Pydantic Models for API Requests
# ============================================================================

class TranslationRequest(BaseModel):
    """Request model for language translation"""
    text: str
    target_language: str
    choice: int = 4  # Default to template-based chain

class WeatherRequest(BaseModel):
    """Request model for weather information"""
    query: str

class TripPlanRequest(BaseModel):
    """Request model for trip planning"""
    origin: str
    cities: str
    date_range: str
    interests: str

class EmailRequest(BaseModel):
    """Request model for email sending"""
    to: str
    subject: str
    body: str

class CalendarEventRequest(BaseModel):
    """Request model for calendar event creation"""
    summary: str
    start_time: str  # YYYY-MM-DD HH:MM
    end_time: str    # YYYY-MM-DD HH:MM
    description: str = ""
    location: str = ""

class MCPQueryRequest(BaseModel):
    """Request model for MCP database queries"""
    query: str

# ============================================================================
# Observability & Metrics
# ============================================================================

class MetricsCollector:
    """Collects application metrics"""
    
    def __init__(self):
        self.requests_total = 0
        self.requests_by_endpoint = {}
        self.errors_total = 0
        self.active_sessions = set()
        self.start_time = datetime.now()
    
    def record_request(self, endpoint: str):
        """Record an API request"""
        self.requests_total += 1
        self.requests_by_endpoint[endpoint] = self.requests_by_endpoint.get(endpoint, 0) + 1
    
    def record_error(self):
        """Record an error"""
        self.errors_total += 1
    
    def add_session(self, session_id: str):
        """Add active session"""
        self.active_sessions.add(session_id)
    
    def remove_session(self, session_id: str):
        """Remove active session"""
        self.active_sessions.discard(session_id)
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "uptime_seconds": uptime,
            "requests_total": self.requests_total,
            "requests_by_endpoint": self.requests_by_endpoint,
            "errors_total": self.errors_total,
            "active_sessions": len(self.active_sessions),
            "error_rate": self.errors_total / max(self.requests_total, 1)
        }

metrics = MetricsCollector()

# ============================================================================
# ADK Agent Session Management
# ============================================================================

def start_agent_session(session_id: str, is_audio: bool = False):
    """
    Starts an ADK agent session with Jarvis
    
    Args:
        session_id: Unique session identifier
        is_audio: Whether to enable audio mode
    
    Returns:
        Tuple of (live_events, live_request_queue)
    """
    logger.info(f"Starting agent session: {session_id}, audio={is_audio}")
    
    # Create a Session
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )
    
    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=jarvis_agent,
        session_service=session_service,
    )
    
    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"
    
    # Create speech config with voice settings
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
        )
    )
    
    # Create run config
    config = {"response_modalities": [modality], "speech_config": speech_config}
    
    # Add output_audio_transcription when audio is enabled
    if is_audio:
        config["output_audio_transcription"] = {}
    
    run_config = RunConfig(**config)
    
    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()
    
    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    
    metrics.add_session(session_id)
    return live_events, live_request_queue

async def agent_to_client_messaging(
    websocket: WebSocket, live_events: AsyncIterable[Event | None]
):
    """
    Handles agent to client communication
    Streams responses from agent to client via WebSocket
    """
    while True:
        async for event in live_events:
            if event is None:
                continue
            
            # Handle turn complete or interrupted
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Turn complete: {message}")
                continue
            
            # Read the Content and its first Part
            part = event.content and event.content.parts and event.content.parts[0]
            if not part or not isinstance(part, types.Part):
                continue
            
            # Send text if it's a partial response (streaming)
            if part.text and event.partial:
                message = {
                    "mime_type": "text/plain",
                    "data": part.text,
                    "role": "model",
                }
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Sent text: {part.text[:50]}...")
            
            # Send audio if available
            is_audio = (
                part.inline_data
                and part.inline_data.mime_type
                and part.inline_data.mime_type.startswith("audio/pcm")
            )
            if is_audio:
                audio_data = part.inline_data and part.inline_data.data
                if audio_data:
                    message = {
                        "mime_type": "audio/pcm",
                        "data": base64.b64encode(audio_data).decode("ascii"),
                        "role": "model",
                    }
                    await websocket.send_text(json.dumps(message))
                    logger.debug(f"Sent audio: {len(audio_data)} bytes")

async def client_to_agent_messaging(
    websocket: WebSocket, live_request_queue: LiveRequestQueue
):
    """
    Handles client to agent communication
    Receives messages from client and forwards to agent
    """
    while True:
        # Decode JSON message
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]
        role = message.get("role", "user")
        
        # Send the message to the agent
        if mime_type == "text/plain":
            content = types.Content(role=role, parts=[types.Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            logger.info(f"User message: {data}")
        elif mime_type == "audio/pcm":
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(
                types.Blob(data=decoded_data, mime_type=mime_type)
            )
            logger.debug(f"Received audio: {len(decoded_data)} bytes")
        else:
            raise ValueError(f"Mime type not supported: {mime_type}")

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Serves the main application UI"""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse({
        "message": "Enterprise Gen AI Multi-Agent System",
        "version": APP_VERSION,
        "frameworks": ["ADK", "LangChain", "CrewAI"],
        "docs": "/docs"
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """Get application metrics"""
    return metrics.get_metrics()

@app.get("/api/info")
async def get_info():
    """Get application information and available agents"""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "frameworks": {
            "jarvis_adk": {
                "name": "Jarvis ADK",
                "framework": "Google ADK",
                "capabilities": [
                    "Calendar management",
                    "Trip planning",
                    "Email sending",
                    "Voice interaction"
                ],
                "tools": [
                    "list_events",
                    "create_event",
                    "edit_event",
                    "delete_event",
                    "plan_trip",
                    "send_email"
                ]
            },
            "lenny_lang": {
                "name": "Lenny Lang",
                "framework": "LangChain",
                "capabilities": [
                    "Language translation",
                    "Weather information",
                    "LCEL patterns"
                ],
                "agents": [
                    "Language Translation Agent",
                    "Weather Agent with Guardrails"
                ]
            },
            "taylor_crew": {
                "name": "Taylor Crew",
                "framework": "CrewAI",
                "capabilities": [
                    "Multi-agent trip planning",
                    "Email automation",
                    "Agent orchestration"
                ],
                "crews": [
                    "Trip Planner Crew",
                    "Email Processing Crew"
                ]
            },
            "mcp": {
                "name": "MCP Tools",
                "framework": "Model Context Protocol",
                "capabilities": [
                    "Database operations",
                    "Custom tool servers"
                ]
            },
            "a2a": {
                "name": "A2A Protocol",
                "framework": "Agent-to-Agent",
                "capabilities": [
                    "Agent collaboration",
                    "Multi-agent scheduling"
                ]
            }
        }
    }

# ============================================================================
# Jarvis ADK Endpoints
# ============================================================================

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    is_audio: str = Query("false"),
):
    """
    WebSocket endpoint for real-time agent interaction
    Supports both text and audio streaming
    """
    await websocket.accept()
    logger.info(f"Client #{session_id} connected, audio mode: {is_audio}")
    
    try:
        # Start agent session
        live_events, live_request_queue = start_agent_session(
            session_id, is_audio == "true"
        )
        
        # Start bidirectional messaging tasks
        agent_to_client_task = asyncio.create_task(
            agent_to_client_messaging(websocket, live_events)
        )
        client_to_agent_task = asyncio.create_task(
            client_to_agent_messaging(websocket, live_request_queue)
        )
        
        await asyncio.gather(agent_to_client_task, client_to_agent_task)
        
    except WebSocketDisconnect:
        logger.info(f"Client #{session_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        metrics.record_error()
    finally:
        metrics.remove_session(session_id)

# ============================================================================
# Lenny Lang Endpoints (LangChain)
# ============================================================================

@app.post("/api/lenny/translate")
async def translate_text(request: TranslationRequest):
    """
    Translate text using LangChain agent
    
    Supports 4 different LCEL patterns:
    1. Basic message chain
    2. With output parser
    3. Chained model + parser
    4. Template-based chain (recommended)
    """
    metrics.record_request("/api/lenny/translate")
    
    try:
        # Import here to avoid startup dependencies
        from app.lenny_lang.language_agent.language_expert import initialize_llm, behaviour_llm
        
        llm = initialize_llm()
        result = behaviour_llm(
            llm,
            request.choice,
            request.target_language,
            request.text
        )
        
        return {
            "status": "success",
            "original_text": request.text,
            "target_language": request.target_language,
            "translated_text": result,
            "method": f"LCEL Pattern {request.choice}"
        }
    except Exception as e:
        logger.error(f"Translation error: {e}")
        metrics.record_error()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/lenny/weather")
async def get_weather(request: WeatherRequest):
    """
    Get weather information using LangChain agent with guardrails
    
    The agent first checks if the query is weather-related,
    then fetches real-time weather data if allowed.
    """
    metrics.record_request("/api/lenny/weather")
    
    try:
        from app.lenny_lang.weather_agent.weather_agent import (
            initialize_llm,
            check_guardrails,
            create_weather_agent
        )
        
        llm = initialize_llm()
        
        # Check guardrails
        is_allowed = check_guardrails(request.query, llm)
        
        if not is_allowed:
            return {
                "status": "blocked",
                "message": "Query is not weather-related",
                "query": request.query
            }
        
        # Create and run weather agent
        agent_executor = create_weather_agent(llm)
        response = agent_executor.invoke({"input": request.query})
        
        return {
            "status": "success",
            "query": request.query,
            "response": response['output']
        }
    except Exception as e:
        logger.error(f"Weather error: {e}")
        metrics.record_error()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Taylor Crew Endpoints (CrewAI)
# ============================================================================

@app.post("/api/taylor/plan-trip")
async def plan_trip(request: TripPlanRequest):
    """
    Plan a trip using CrewAI multi-agent system
    
    Orchestrates three agents:
    - City Selector: Chooses best destination
    - Local Expert: Gathers city information
    - Travel Concierge: Creates detailed itinerary
    """
    metrics.record_request("/api/taylor/plan-trip")
    
    try:
        from app.taylor_crew.trip_planner.main import TripCrew
        
        logger.info(f"Starting trip planning: {request.cities}")
        
        # Create and run trip crew
        crew = TripCrew(
            request.origin,
            request.cities,
            request.date_range,
            request.interests
        )
        
        result = crew.run()
        
        return {
            "status": "success",
            "origin": request.origin,
            "cities": request.cities,
            "date_range": request.date_range,
            "interests": request.interests,
            "trip_plan": str(result)
        }
    except Exception as e:
        logger.error(f"Trip planning error: {e}")
        metrics.record_error()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/taylor/process-emails")
async def process_emails():
    """
    Process emails using CrewAI + LangGraph workflow
    
    Workflow:
    1. Check emails from Gmail
    2. Analyze email content and priority
    3. Generate draft responses
    4. Save drafts to Gmail
    """
    metrics.record_request("/api/taylor/process-emails")
    
    try:
        from app.taylor_crew.e_mail_crew.main import app as email_app
        
        logger.info("Starting email processing workflow")
        
        result = email_app.invoke({})
        
        return {
            "status": "success",
            "message": "Email processing completed",
            "result": str(result)
        }
    except Exception as e:
        logger.error(f"Email processing error: {e}")
        metrics.record_error()
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Utility Endpoints
# ============================================================================

@app.get("/api/frameworks")
async def list_frameworks():
    """List all available frameworks and their capabilities"""
    return {
        "frameworks": [
            {
                "id": "jarvis_adk",
                "name": "Jarvis ADK",
                "framework": "Google ADK",
                "description": "Voice-enabled calendar and productivity assistant",
                "endpoints": ["/ws/{session_id}"]
            },
            {
                "id": "lenny_lang",
                "name": "Lenny Lang",
                "framework": "LangChain",
                "description": "Language translation and weather information",
                "endpoints": ["/api/lenny/translate", "/api/lenny/weather"]
            },
            {
                "id": "taylor_crew",
                "name": "Taylor Crew",
                "framework": "CrewAI",
                "description": "Multi-agent trip planning and email automation",
                "endpoints": ["/api/taylor/plan-trip", "/api/taylor/process-emails"]
            }
        ]
    }

# ============================================================================
# Application Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info("Frameworks: ADK, LangChain, CrewAI")
    logger.info(f"Documentation: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info(f"Shutting down {APP_NAME}")
    logger.info(f"Total requests processed: {metrics.requests_total}")

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
