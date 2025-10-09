
import os
import re
import shutil
import atexit
import json
import asyncio
import socket
import signal
import sys
import base64
from typing import List, Dict, Any
import yaml
import numpy as np
import chardet
from loguru import logger
from fastapi import FastAPI, WebSocket, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocketDisconnect
from pydantic import BaseModel
from module.openllm_vtuber_main import OpenLLMVTuberMain
from module.live2d_model import Live2dModel
from tts.stream_audio import AudioPayloadPreparer
from port_config import get_available_port, cleanup_ports, get_current_port
import argparse

# Enhanced Vision + RAG Pipeline
try:
    from vision_rag_pipeline import VisionRAGPipeline, enhance_vision_analysis_with_rag
    VISION_RAG_AVAILABLE = True
    logger.info("[Vision RAG] Vision + RAG pipeline available")
except ImportError:
    VISION_RAG_AVAILABLE = False
    logger.warning("[Vision RAG] Vision + RAG pipeline not available")

# Enhanced RAG imports
try:
    from aws_knowledge_base_rag import AWSKnowledgeBaseRAG, HybridRAGSystem, create_rag_system
    AWS_KB_RAG_AVAILABLE = True
    logger.info("[AWS KB RAG] AWS Knowledge Base RAG system available")
except ImportError:
    AWS_KB_RAG_AVAILABLE = False
    logger.warning("[AWS KB RAG] AWS Knowledge Base RAG not available")

# Import existing RAG functionality for fallback
try:
    from demo_rag_client import DemoManufacturingRAG, ManufacturingContext
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("[RAG] Warning: Local RAG functionality not available")

# Import Simple S3 RAG for Claude integration
try:
    from simple_s3_rag import SimpleS3RAG
    S3_RAG_AVAILABLE = True
    logger.info("[RAG] Simple S3 RAG system available")
except ImportError:
    S3_RAG_AVAILABLE = False
    logger.warning("[RAG] Warning: Simple S3 RAG not available")


def find_available_port(start_port: int = 1025, max_attempts: int = 25) -> int:
    """
    Find an available port starting from start_port.
    
    Args:
        start_port: Port to start checking from (default: 1025)
        max_attempts: Maximum number of ports to check (default: 25)
        
    Returns:
        An available port number
        
    Raises:
        RuntimeError: If no available ports are found after max_attempts
    """
    used_ports = set()
    
    for port_offset in range(max_attempts):
        port = start_port + port_offset
        try:
            # Try to create a socket with the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                logger.info(f"Found available port: {port}")
                return port
        except socket.error:
            used_ports.add(port)
            logger.warning(f"Port {port} is in use, trying next port")
    
    # If we've tried all ports and none are available, raise an exception
    logger.error(f"All ports in range {start_port}-{start_port + max_attempts - 1} are in use: {sorted(used_ports)}")
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts in range {start_port}-{start_port + max_attempts - 1}")


def load_enhanced_rag_context_for_vision(user_question: str = "", image_analysis_preview: str = "") -> str:
    """Enhanced RAG context loading with AWS Knowledge Base support"""
    
    # Try AWS Knowledge Base first
    if AWS_KB_RAG_AVAILABLE:
        try:
            aws_rag = AWSKnowledgeBaseRAG()
            if aws_rag.is_available():
                search_query = f"{user_question} {image_analysis_preview}".strip()
                if not search_query:
                    search_query = "manufacturing error analysis equipment defect"
                
                response = aws_rag.get_rag_response(search_query, max_results=3)
                
                if response.sources_used > 0:
                    rag_context = "\n\n=== AWS KNOWLEDGE BASE ===\n"
                    rag_context += f"Retrieved {response.sources_used} relevant documents:\n\n"
                    
                    for i, doc in enumerate(response.documents, 1):
                        safety_indicator = "⚠️ " if any(keyword in doc.content.lower() 
                                                     for keyword in ["safety", "critical", "warning"]) else ""
                        rag_context += f"{i}. {safety_indicator}{doc.source} (Score: {doc.score:.3f})\n"
                        rag_context += f"   {doc.content[:400]}...\n\n"
                    
                    rag_context += "=== END KNOWLEDGE BASE ===\n\n"
                    logger.info(f"[AWS KB RAG] Enhanced vision context with {response.sources_used} documents")
                    return rag_context
                else:
                    logger.info("[AWS KB RAG] No relevant documents found, falling back to local RAG")
        except Exception as e:
            logger.warning(f"[AWS KB RAG] Error: {e}, falling back to local RAG")
    
    # Fallback to existing local RAG
    if not RAG_AVAILABLE:
        return ""
    
    try:
        # Initialize RAG client
        rag_client = DemoManufacturingRAG()
        
        # Create search query from user question and any initial image analysis
        search_query = f"{user_question} {image_analysis_preview}".strip()
        if not search_query:
            search_query = "manufacturing error analysis equipment defect"
        
        # Get relevant context from RAG
        context = rag_client.get_context(search_query)
        
        if context and hasattr(context, 'relevant_docs') and context.relevant_docs:
            rag_context = "\n\n=== LOCAL MANUFACTURING KNOWLEDGE BASE ===\n"
            rag_context += "Based on your manufacturing documentation, here is relevant context:\n\n"
            
            for doc in context.relevant_docs[:3]:  # Use top 3 most relevant documents
                rag_context += f"• {doc.get('content', '')[:500]}...\n\n"
            
            rag_context += "=== END KNOWLEDGE BASE ===\n\n"
            logger.info(f"[Local RAG] Enhanced vision context with {len(context.relevant_docs)} documents")
            return rag_context
        
    except Exception as e:
        logger.warning(f"[Local RAG] Could not load RAG context: {e}")
    
    return ""


def is_manufacturing_mode(config: dict) -> bool:
    """Check if the system is running in manufacturing mode"""
    llm_provider = config.get('LLM_PROVIDER', '').lower()
    persona = config.get('PERSONA_CHOICE', '').lower()
    
    return ('manufacturing' in llm_provider or
            'manufacturing' in persona or
            llm_provider == 'manufacturing_rag')


def load_local_rag_documents() -> str:
    """Load local RAG documents as fallback"""
    try:
        import json
        from pathlib import Path
        
        # Try to load the local RAG index
        index_file = Path("rag_documents_index.json")
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            documents = index_data.get('documents', [])
            if documents:
                context = "\n\n=== MANUFACTURING DOCUMENTATION ===\n"
                context += "Relevant manufacturing error documentation:\n\n"
                
                # Include relevant documents (limit to avoid token overflow)
                for doc in documents[:2]:  # Use first 2 documents
                    title = doc.get('title', 'Manufacturing Documentation')
                    content = doc.get('content', '')[:1000]  # Limit content length
                    context += f"**{title}**\n{content}...\n\n"
                
                context += "=== END DOCUMENTATION ===\n\n"
                return context
        
        # Fallback: Load documents directly from rag_documents folder
        rag_dir = Path("rag_documents")
        if rag_dir.exists():
            context = "\n\n=== MANUFACTURING KNOWLEDGE ===\n"
            
            # Load heater error documentation specifically
            heater_doc = rag_dir / "heater_error_103_documentation.md"
            if heater_doc.exists():
                with open(heater_doc, 'r', encoding='utf-8') as f:
                    content = f.read()[:2000]  # Limit to avoid token overflow
                    context += f"Heater Error Documentation:\n{content}...\n\n"
            
            context += "=== END KNOWLEDGE ===\n\n"
            return context
            
    except Exception as e:
        logger.warning(f"[RAG] Could not load local RAG documents: {e}")
    
    return ""


def _create_concise_vision_summary(full_response: str, user_question: str) -> str:
    """
    Create an extremely concise summary from Claude's detailed vision analysis.
    
    Args:
        full_response: Claude's full detailed analysis
        user_question: The original user question
        
    Returns:
        A very brief summary (e.g., "a can of Pepsi") with offer to elaborate
    """
    try:
        # Clean the response text and remove Live2D emotion tags
        response = full_response.strip()
        # Remove emotion tags like [neutral], [joy], etc.
        import re
        response = re.sub(r'\[[\w\s]+\]', '', response).strip()
        
        response_lower = response.lower()
        
        # Extract the most basic object identification
        concise_id = ""
        
        # Look for specific brand/product mentions
        if 'pepsi' in response_lower:
            concise_id = "a can of Pepsi"
        elif 'coca cola' in response_lower or 'coke' in response_lower:
            concise_id = "a can of Coca-Cola"
        elif 'sprite' in response_lower:
            concise_id = "a can of Sprite"
        elif 'playstation' in response_lower and ('controller' in response_lower or 'ps5' in response_lower or 'ps4' in response_lower):
            concise_id = "a PlayStation controller"
        elif 'xbox' in response_lower and 'controller' in response_lower:
            concise_id = "an Xbox controller"
        elif 'nintendo' in response_lower and ('controller' in response_lower or 'switch' in response_lower):
            concise_id = "a Nintendo controller"
        elif 'keyboard' in response_lower:
            concise_id = "a keyboard"
        elif 'mouse' in response_lower:
            concise_id = "a computer mouse"
        elif 'phone' in response_lower or 'smartphone' in response_lower:
            concise_id = "a smartphone"
        elif 'tablet' in response_lower:
            concise_id = "a tablet"
        elif 'remote' in response_lower:
            concise_id = "a remote control"
        elif 'headphones' in response_lower:
            concise_id = "headphones"
        elif 'bottle' in response_lower:
            concise_id = "a bottle"
        elif 'can' in response_lower and 'beverage' in response_lower:
            concise_id = "a beverage can"
        elif 'controller' in response_lower or 'gamepad' in response_lower:
            concise_id = "a gaming controller"
        else:
            # Generic fallback - look for first noun after common identifiers
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            if sentences:
                first_sentence = sentences[0].lower()
                if 'this is' in first_sentence:
                    # Extract what comes after "this is"
                    parts = first_sentence.split('this is')
                    if len(parts) > 1:
                        object_part = parts[1].strip()
                        # Take first few words
                        words = object_part.split()[:3]
                        concise_id = ' '.join(words)
                        if not concise_id.startswith(('a ', 'an ')):
                            concise_id = f"a {concise_id}"
                
                if not concise_id:
                    concise_id = "an object"
        
        # Create final response with offer to elaborate
        summary = f"{concise_id}. Would you like me to tell you more about it?"
        
        return summary
        
    except Exception as e:
        logger.error(f"[VISION TTS] Error creating concise summary: {e}")
        return "I can see an object. Would you like me to tell you more about it?"


class WebSocketServer:
    """
    Enhanced WebSocketServer with AWS Knowledge Base RAG integration
    """

    def __init__(self, open_llm_vtuber_main_config: Dict | None = None, web=False):
        """
        Initializes the WebSocketServer with the given configuration.

        Parameters:
            open_llm_vtuber_main_config (dict): Configuration dictionary.
            web (bool): Whether to mount static files.
        """
        self.app = FastAPI()
        self.router = APIRouter()
        self.connected_clients: List[WebSocket] = []
        self.open_llm_vtuber_main_config = open_llm_vtuber_main_config

        # Initialize Enhanced RAG System
        self.rag_system = None
        if AWS_KB_RAG_AVAILABLE:
            try:
                self.rag_system = create_rag_system(self.open_llm_vtuber_main_config)
                logger.info("[Enhanced RAG] Hybrid RAG system initialized")
                
                # Log RAG system status
                health = self.rag_system.health_check()
                logger.info(f"[Enhanced RAG] System status: {json.dumps(health, indent=2)}")
            except Exception as e:
                logger.error(f"[Enhanced RAG] Failed to initialize: {e}")
                self.rag_system = None

        # Add CORS middleware - Updated for Vite development
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",  # Vite dev server
                "http://localhost:3000",  # Alternative dev port
                "http://127.0.0.1:5173", # Alternative localhost
                "http://127.0.0.1:3000", # Alternative localhost
                "*"  # Allow all for development (remove in production)
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info("CORS middleware enabled for Vite development (localhost:5173)")

        # Initialize model manager  
        self.preload_models = self.open_llm_vtuber_main_config.get("SERVER", {}).get(
            "PRELOAD_MODELS", False
        )
        
        # Create model_manager unconditionally to avoid AttributeError
        self.model_manager = None
        if self.preload_models:
            logger.info("Preloading ASR and TTS models...")
            logger.info(
                "Using: " + str(self.open_llm_vtuber_main_config.get("ASR_MODEL"))
            )
            logger.info(
                "Using: " + str(self.open_llm_vtuber_main_config.get("TTS_MODEL"))
            )

        self._setup_routes()
        if web:
            self._mount_static_files()
        self.app.include_router(self.router)

    async def _handle_config_switch(
        self, websocket: WebSocket, config_file: str
    ) -> tuple[Live2dModel, OpenLLMVTuberMain] | None:
        new_config = self._load_config_from_file(config_file)
        if new_config:
            try:
                if self.preload_models:
                    self.model_manager.update_models(new_config)

                self.open_llm_vtuber_main_config.update(new_config)

                loop = asyncio.get_event_loop()
                l2d, open_llm_vtuber, _ = self._initialize_components(websocket, loop)

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "config-switched",
                            "message": f"Switched to config: {config_file}",
                        }
                    )
                )
                await websocket.send_text(
                    json.dumps({"type": "set-model", "text": l2d.model_info})
                )
                logger.info(f"Configuration switched to {config_file}")

                return l2d, open_llm_vtuber

            except Exception as e:
                logger.error(f"Error switching configuration: {e}")
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"Error switching configuration: {str(e)}",
                        }
                    )
                )
                return None
        return None

    def _initialize_components(
        self, websocket: WebSocket, loop
    ) -> tuple[Live2dModel, OpenLLMVTuberMain, AudioPayloadPreparer]:
        """Initialize or reinitialize components with current configuration."""
        # Handle missing LIVE2D_MODEL configuration gracefully
        live2d_model = self.open_llm_vtuber_main_config.get("LIVE2D_MODEL", "default")
        l2d = Live2dModel(live2d_model)

        # Use cached models if available
        custom_asr = (
            self.model_manager.cache.get("asr") if self.preload_models else None
        )
        custom_tts = (
            self.model_manager.cache.get("tts") if self.preload_models else None
        )

        open_llm_vtuber = OpenLLMVTuberMain(
            self.open_llm_vtuber_main_config,
            custom_asr=custom_asr,
            custom_tts=custom_tts,
            loop = loop
        )

        audio_preparer = AudioPayloadPreparer()

        # Set up the audio playback function
        def _websocket_audio_handler(
            sentence: str | None,
            filepath: str | None,
            instrument_filepath: str | None = None
        ) -> None:
            if filepath is None:
                logger.info("No audio to be streamed. Response is empty.")
                return

            if sentence is None:
                sentence = ""

            logger.info(f"Playing {filepath}...")
            logger.info(f"Preparing audio payload for text: {sentence[:50]}...")
            
            try:
                payload, duration = audio_preparer.prepare_audio_payload(
                    audio_path=filepath,
                    instrument_path=instrument_filepath,
                    display_text=sentence,
                    expression_list=l2d.extract_emotion(sentence),
                )
                # Ensure proper message type for frontend audio handler
                payload["type"] = payload.get("type", "audio-payload")
                payload.setdefault("format", "mp3")
                
                # Add debugging info
                logger.info(f"Payload prepared - Type: {payload.get('type')}, Format: {payload.get('format')}")
                logger.info(f"Audio size: {len(payload.get('audio', ''))} bytes, Text: {sentence[:30]}...")
                
                async def _send_audio():
                    try:
                        # Check WebSocket state before sending
                        if websocket.client_state.value == 1:  # 1 = CONNECTED state
                            await websocket.send_text(json.dumps(payload))
                            logger.info(f"✅ Successfully sent audio payload with text: {sentence[:50]}...")
                            await asyncio.sleep(duration)
                        else:
                            logger.error(f"❌ WebSocket not connected. State: {websocket.client_state}")
                    except Exception as e:
                        logger.error(f"❌ Failed to send audio payload: {e}")
                        logger.error(f"Error type: {type(e).__name__}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")

                # Fix: Use run_coroutine_threadsafe which works from non-async context
                try:
                    if loop:
                        # This is being called from a non-async context (TTS callback)
                        # so we must use run_coroutine_threadsafe
                        future = asyncio.run_coroutine_threadsafe(_send_audio(), loop)
                        try:
                            # Wait for completion with timeout
                            future.result(timeout=5)
                            logger.info("✅ Audio payload sent successfully via run_coroutine_threadsafe")
                        except Exception as e:
                            logger.error(f"❌ WebSocket send failed: {e}")
                    else:
                        logger.error("❌ No event loop available to send audio")
                except Exception as e:
                    logger.error(f"❌ Failed to schedule audio send: {e}")
                
                logger.info("Audio handler completed")
                
            except Exception as e:
                logger.error(f"❌ Error in audio handler: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")

        open_llm_vtuber.set_audio_output_func(
            lambda sentence, filepath, instrument_filepath=None: _websocket_audio_handler(
                sentence, filepath, instrument_filepath
            )
        )
        return l2d, open_llm_vtuber, audio_preparer

    def _setup_routes(self):
        """Sets up the WebSocket and broadcast routes with enhanced RAG support."""

        # Health check endpoint - Enhanced for Vite proxy
        @self.app.get("/health")
        async def health_check():
            health_data = {
                "status": "ok",
                "message": "Server is running",
                "port": get_current_port() or 8000,
                "timestamp": asyncio.get_event_loop().time(),
                "version": "1.0.0"
            }
            
            # Add RAG system health
            if self.rag_system:
                health_data["rag_system"] = self.rag_system.health_check()
            
            return health_data

        # Enhanced RAG health endpoint
        @self.app.get("/rag/health")
        async def rag_health_check():
            if not self.rag_system:
                return {"status": "disabled", "message": "RAG system not available"}
            
            return self.rag_system.health_check()

        # Mock TTS endpoint for development
        class TTSRequest(BaseModel):
            text: str
            voice: str = "en-US-JennyNeural"
            rate: str = "+0%"
            pitch: str = "+0Hz"

        @self.app.post("/api/tts/mock")
        async def mock_tts_endpoint(request: TTSRequest):
            """Mock TTS endpoint for frontend development"""
            logger.info(f"Mock TTS request: {request.text[:50]}...")
            return {
                "status": "success",
                "message": "Mock TTS generated",
                "text": request.text,
                "voice": request.voice,
                "audio_length": len(request.text) * 0.1,  # Mock duration
                "base64": "mock_audio_data_base64_encoded_string"
            }

        # Mock STT endpoint for development
        class STTRequest(BaseModel):
            audio: str  # Base64 encoded audio
            language: str = "en"

        @self.app.post("/api/stt/mock")
        async def mock_stt_endpoint(request: STTRequest):
            """Mock STT endpoint for frontend development"""
            logger.info(f"Mock STT request: {len(request.audio)} bytes")
            return {
                "status": "success",
                "message": "Mock STT processed",
                "text": "This is a mock transcription of your audio input.",
                "confidence": 0.95,
                "language": request.language
            }

        # Enhanced Claude endpoint with AWS Knowledge Base RAG
        class ClaudeRequest(BaseModel):
            text: str
            system: str = "You are a helpful manufacturing assistant."
            messages: List[Dict[str, str]] = []
            image: str = None
            has_vision: bool = False
            enable_rag: bool = True
            rag_mode: str = "hybrid"  # aws, local, hybrid

        @self.app.post("/claude")
        async def claude_endpoint(request: ClaudeRequest):
            """Enhanced Claude API endpoint with AWS Knowledge Base RAG integration"""
            try:
                logger.info(f"[Enhanced Claude] Processing request: {request.text[:100]}...")
                
                # Enhanced RAG context retrieval
                rag_context = ""
                rag_metadata = {
                    "sources_used": 0,
                    "rag_enabled": request.enable_rag,
                    "rag_mode": request.rag_mode,
                    "retrieval_time": 0.0
                }
                
                if request.enable_rag and self.rag_system and not request.has_vision:
                    try:
                        logger.info(f"[Enhanced RAG] Retrieving context for: {request.text[:50]}...")
                        rag_response = self.rag_system.get_context(request.text)
                        
                        if rag_response.sources_used > 0:
                            rag_context = rag_response.enhanced_prompt
                            rag_metadata.update({
                                "sources_used": rag_response.sources_used,
                                "retrieval_time": rag_response.retrieval_time,
                                "knowledge_base_id": rag_response.knowledge_base_id,
                                "sources": [{"source": doc.source, "score": doc.score} 
                                          for doc in rag_response.documents]
                            })
                            logger.info(f"[Enhanced RAG] Enhanced prompt with {rag_response.sources_used} documents from {rag_response.knowledge_base_id}")
                        else:
                            logger.info("[Enhanced RAG] No relevant documents found")
                            rag_context = request.text
                    except Exception as e:
                        logger.error(f"[Enhanced RAG] Error: {e}")
                        rag_context = request.text
                else:
                    rag_context = request.text

                # Here you would call your actual Claude API
                # For now, return a mock response with RAG metadata
                mock_response = f"Enhanced response based on your query: {request.text}"
                if rag_metadata["sources_used"] > 0:
                    mock_response = f"Based on the manufacturing documentation, {mock_response}"

                return {
                    "reply": mock_response,
                    "rag_metadata": rag_metadata,
                    "enhanced_prompt_length": len(rag_context),
                    "original_query": request.text
                }

            except Exception as e:
                logger.error(f"[Enhanced Claude] Error: {e}")
                return {
                    "error": str(e),
                    "rag_metadata": rag_metadata
                }

        # WebSocket echo endpoint for connection testing
        @self.app.websocket("/ws/echo")
        async def websocket_echo(websocket: WebSocket):
            """WebSocket echo endpoint for connection testing"""
            await websocket.accept()
            logger.info("WebSocket echo connection established")
            
            try:
                while True:
                    data = await websocket.receive_text()
                    logger.info(f"Echo received: {data}")
                    
                    try:
                        message = json.loads(data)
                        echo_response = {
                            "type": "echo",
                            "original": message,
                            "timestamp": asyncio.get_event_loop().time()
                        }
                        await websocket.send_text(json.dumps(echo_response))
                    except json.JSONDecodeError:
                        await websocket.send_text(f"Echo: {data}")
                        
            except WebSocketDisconnect:
                logger.info("WebSocket echo connection closed")

        # Test audio payload endpoint
        @self.app.post("/test-audio-payload")
        async def test_audio_payload():
            """Test endpoint for audio payload generation"""
            try:
                # Create a simple test audio payload
                test_payload = {
                    "type": "audio-payload",
                    "format": "mp3",
                    "audio": "test_audio_data_base64",
                    "text": "This is a test audio message",
                    "duration": 2.5,
                    "expressions": ["neutral"]
                }
                return {"status": "success", "payload": test_payload}
            except Exception as e:
                return {"status": "error", "message": str(e)}

        # Main WebSocket endpoint with enhanced RAG support
        @self.app.websocket("/client-ws")
        async def websocket_endpoint(websocket: WebSocket):
            loop = asyncio.get_event_loop()
            await websocket.accept()
            self.connected_clients.append(websocket)
            logger.info(f"WebSocket connection established. Total clients: {len(self.connected_clients)}")

            # Initialize components
            l2d, open_llm_vtuber, audio_preparer = self._initialize_components(websocket, loop)

            # Send initial model info
            await websocket.send_text(
                json.dumps({"type": "set-model", "text": l2d.model_info})
            )

            # Send available config files
            config_files = self._scan_config_alts_directory()
            await websocket.send_text(
                json.dumps({"type": "config-list", "configs": config_files})
            )

            # Send background options
            bg_files = self._scan_bg_directory()
            await websocket.send_text(
                json.dumps({"type": "bg-list", "backgrounds": bg_files})
            )

            # Send RAG system status
            if self.rag_system:
                rag_status = self.rag_system.health_check()
                await websocket.send_text(
                    json.dumps({"type": "rag-status", "status": rag_status})
                )

            try:
                while True:
                    try:
                        data = await websocket.receive_text()
                        print(".", end="")
                        
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError:
                            logger.error("Invalid JSON received")
                            continue

                        message_type = data.get("type")
                        
                        # Handle different message types
                        if message_type == "config-switch":
                            config_file = data.get("config")
                            result = await self._handle_config_switch(websocket, config_file)
                            if result:
                                l2d, open_llm_vtuber = result

                        elif message_type == "bg-switch":
                            bg_file = data.get("background")
                            await websocket.send_text(
                                json.dumps({"type": "bg-switched", "background": bg_file})
                            )

                        elif message_type == "interrupt":
                            heard_sentence = data.get("heardSentence", "")
                            open_llm_vtuber.interrupt(heard_sentence)

                        elif message_type == "audio-data-end":
                            print("\n[STT DEBUG] Received audio data end from front end.")
                            
                            # Enhanced conversation with RAG support
                            async def _run_conversation():
                                try:
                                    await websocket.send_text(
                                        json.dumps({"type": "conversation-thinking"})
                                    )
                                    
                                    # Get user input from audio data
                                    user_input = data.get("text", "")
                                    if not user_input:
                                        logger.warning("No text provided in audio data")
                                        return
                                    
                                    # Enhanced RAG processing
                                    if self.rag_system:
                                        try:
                                            rag_response = self.rag_system.get_context(user_input)
                                            if rag_response.sources_used > 0:
                                                # Use enhanced prompt for conversation
                                                conversation_result = open_llm_vtuber.conversation_chain(rag_response.enhanced_prompt)
                                            else:
                                                conversation_result = open_llm_vtuber.conversation_chain(user_input)
                                        except Exception as e:
                                            logger.error(f"[Enhanced RAG] Error in conversation: {e}")
                                            conversation_result = open_llm_vtuber.conversation_chain(user_input)
                                    else:
                                        conversation_result = open_llm_vtuber.conversation_chain(user_input)
                                    
                                    await websocket.send_text(
                                        json.dumps({"type": "conversation-done"})
                                    )
                                    
                                except Exception as e:
                                    logger.error(f"[Conversation] Error: {e}")
                                    await websocket.send_text(
                                        json.dumps({"type": "conversation-error", "error": str(e)})
                                    )
                            
                            # Run conversation in background
                            asyncio.create_task(_run_conversation())

                        elif message_type == "object-analysis-request":
                            try:
                                analysis_id = data.get("analysisId")
                                image_data = data.get("imageData")
                                user_question = data.get("userQuestion", "")
                                
                                if not image_data:
                                    await websocket.send_text(json.dumps({
                                        "type": "object-analysis-result",
                                        "analysisId": analysis_id,
                                        "error": "No image data provided"
                                    }))
                                    continue
                                
                                logger.info(f"[VISION RAG] Starting two-stage Vision + RAG analysis...")
                                
                                try:
                                    # Use the new Vision + RAG pipeline
                                    if VISION_RAG_AVAILABLE:
                                        logger.info(f"[VISION RAG] Using enhanced Vision + RAG pipeline")
                                        
                                        # Get Knowledge Base ID from environment
                                        kb_id = os.environ.get("AWS_KNOWLEDGE_BASE_ID", "HVTKAK0Q86")
                                        
                                        # Process image with Vision + RAG pipeline
                                        pipeline_result = enhance_vision_analysis_with_rag(
                                            image_data=image_data,
                                            user_question=user_question,
                                            knowledge_base_id=kb_id
                                        )
                                        
                                        if pipeline_result.get("pipeline_success"):
                                            vision_info = pipeline_result.get("vision_analysis", {})
                                            rag_info = pipeline_result.get("rag_context", {})
                                            enhanced_response = pipeline_result.get("enhanced_response", "")
                                            
                                            # Create concise summary for TTS
                                            concise_summary = self._create_vision_rag_summary(
                                                vision_info, rag_info, user_question
                                            )
                                            
                                            await websocket.send_text(json.dumps({
                                                "type": "object-analysis-result",
                                                "analysisId": analysis_id,
                                                "result": concise_summary,
                                                "fullAnalysis": enhanced_response,
                                                "visionAnalysis": vision_info,
                                                "ragContext": {
                                                    "sourcesUsed": rag_info.get("sources_used", 0),
                                                    "searchQuery": rag_info.get("search_query", ""),
                                                    "relevantDocs": len(rag_info.get("relevant_docs", []))
                                                },
                                                "pipelineUsed": "vision_rag",
                                                "timestamp": asyncio.get_event_loop().time()
                                            }))
                                            
                                            logger.info(f"[VISION RAG] ✅ Enhanced analysis completed - Vision + {rag_info.get('sources_used', 0)} RAG sources")
                                        else:
                                            # Fallback to basic vision analysis
                                            error_msg = pipeline_result.get("error", "Pipeline failed")
                                            logger.warning(f"[VISION RAG] Pipeline failed: {error_msg}, using fallback")
                                            
                                            await websocket.send_text(json.dumps({
                                                "type": "object-analysis-result",
                                                "analysisId": analysis_id,
                                                "result": "I can see an object in the image. Would you like me to tell you more about it?",
                                                "fullAnalysis": f"Vision + RAG pipeline encountered an issue: {error_msg}",
                                                "pipelineUsed": "fallback",
                                                "timestamp": asyncio.get_event_loop().time()
                                            }))
                                    else:
                                        # Fallback to original vision analysis
                                        logger.info(f"[VISION] Using original vision analysis (Vision RAG not available)")
                                        
                                        # Original vision analysis code
                                        rag_context = load_enhanced_rag_context_for_vision(user_question, "")
                                        
                                        vision_prompt = user_question
                                        if rag_context:
                                            vision_prompt = f"{rag_context}\n\nAnalyze this image: {user_question}"
                                        
                                        vision_response = f"Vision analysis: {vision_prompt[:100]}... [Mock response]"
                                        concise_summary = _create_concise_vision_summary(vision_response, user_question)
                                        
                                        await websocket.send_text(json.dumps({
                                            "type": "object-analysis-result",
                                            "analysisId": analysis_id,
                                            "result": concise_summary,
                                            "fullAnalysis": vision_response,
                                            "ragContextUsed": bool(rag_context),
                                            "pipelineUsed": "original",
                                            "timestamp": asyncio.get_event_loop().time()
                                        }))
                                    
                                except Exception as e:
                                    logger.error(f"[VISION ERROR] ❌ Vision analysis failed: {e}")
                                    await websocket.send_text(json.dumps({
                                        "type": "object-analysis-result",
                                        "analysisId": analysis_id,
                                        "error": f"Vision analysis failed: {str(e)}",
                                        "pipelineUsed": "error"
                                    }))
                                    
                            except Exception as e:
                                logger.error(f"[VISION ERROR] ❌ Critical WebSocket transmission failure: {e}")
                                try:
                                    await websocket.send_text(json.dumps({
                                        "type": "object-analysis-result",
                                        "analysisId": data.get("analysisId"),
                                        "error": f"Critical error: {str(e)}"
                                    }))
                                except Exception as send_error:
                                    logger.error(f"[VISION ERROR] ❌ Failed to send error response: {send_error}")

                    except Exception as e:
                        logger.error(f"Error processing WebSocket message: {e}")
                        
            except WebSocketDisconnect:
                logger.info("WebSocket connection closed")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                if websocket in self.connected_clients:
                    self.connected_clients.remove(websocket)
                logger.info(f"WebSocket connection cleaned up. Remaining clients: {len(self.connected_clients)}")

    def _create_vision_rag_summary(self, vision_info: Dict, rag_info: Dict, user_question: str) -> str:
        """
        Create a concise summary from Vision + RAG analysis for TTS
        
        Args:
            vision_info: Vision analysis results
            rag_info: RAG context results
            user_question: Original user question
            
        Returns:
            Concise summary suitable for TTS
        """
        try:
            # Start with objects detected
            objects = vision_info.get("objects_detected", [])
            if objects:
                object_str = ", ".join(objects[:3])  # Limit to top 3
                summary = f"I can see {object_str}"
            else:
                summary = "I can see an object"
            
            # Add manufacturing relevance
            relevance = vision_info.get("manufacturing_relevance", "")
            if relevance and relevance != "Unknown":
                summary += f" related to {relevance.lower()}"
            
            # Add safety concerns if any
            safety_concerns = vision_info.get("safety_concerns", [])
            if safety_concerns:
                summary += f". ⚠️ Safety note: {safety_concerns[0]} concerns detected"
            
            # Add RAG context if available
            sources_used = rag_info.get("sources_used", 0)
            if sources_used > 0:
                summary += f". Based on our documentation, I found {sources_used} relevant procedures"
                
                # Add key insight from top document
                relevant_docs = rag_info.get("relevant_docs", [])
                if relevant_docs:
                    top_doc = relevant_docs[0]
                    if "safety" in top_doc.get("content", "").lower():
                        summary += " including safety protocols"
                    elif "maintenance" in top_doc.get("content", "").lower():
                        summary += " including maintenance procedures"
                    elif "troubleshooting" in top_doc.get("content", "").lower():
                        summary += " including troubleshooting steps"
            
            # Add offer for more details
            summary += ". Would you like me to provide detailed information?"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating vision RAG summary: {e}")
            return "I can see an object. Would you like me to tell you more about it?"

    def _scan_config_alts_directory(self) -> List[str]:
        config_files = ["conf.yaml"]  # default config file
        
        try:
            config_alts_dir = "config_alts"
            if os.path.exists(config_alts_dir):
                for filename in os.listdir(config_alts_dir):
                    if filename.endswith(('.yaml', '.yml')):
                        config_files.append(filename)
        except Exception as e:
            logger.error(f"Error scanning config_alts directory: {e}")
        
        return config_files

    def _load_config_from_file(self, filename: str) -> Dict:
        """
        Load configuration from a YAML file.
        First tries the config_alts directory, then the current directory.
        """
        config_paths = [
            os.path.join("config_alts", filename),
            filename
        ]
        
        for file_path in config_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'rb') as file:
                        raw_data = file.read()
                        encoding = chardet.detect(raw_data)['encoding']
                except Exception as e:
                    logger.error(f"Error detecting encoding for {file_path}: {e}")
                    continue
                
                try:
                    with open(file_path, "r", encoding=encoding) as file:
                        config = yaml.safe_load(file)
                        logger.info(f"Successfully loaded config from {file_path}")
                        return config
                except Exception as e:
                    logger.error(f"Error loading config from {file_path}: {e}")
                    continue
        
        try:
            # Fallback to environment variables
            config = {}
            for key, value in os.environ.items():
                if key.startswith(('LLM_', 'TTS_', 'ASR_', 'AWS_')):
                    config[key] = value
            
            if config:
                logger.info("Loaded configuration from environment variables")
                return config
        except Exception as e:
            logger.error(f"Error loading config from environment: {e}")
        
        logger.error(f"Could not load configuration from {filename}")
        return {}

    def _scan_bg_directory(self) -> List[str]:
        return []  # Placeholder for background files

    def _mount_static_files(self):
        self.app.mount("/static", StaticFiles(directory="static"), name="static")

    def run(self, host: str = "127.0.0.1", port: int = None, log_level: str = "info"):
        """Runs the FastAPI application using Uvicorn with enhanced RAG support."""
        
        # Log RAG system status at startup
        if self.rag_system:
            logger.info("[Enhanced RAG] System initialized and ready")
            health = self.rag_system.health_check()
            logger.info(f"[Enhanced RAG] Startup health check: {json.dumps(health, indent=2)}")
        else:
            logger.warning("[Enhanced RAG] System not available")
        
        try:
            import uvicorn
            
            if port is None:
                try:
                    actual_port = get_available_port(port)
                except Exception as e:
                    logger.error(f"Error getting available port: {e}")
                    actual_port = find_available_port()
            else:
                actual_port = port
            
            logger.info(f"Starting Enhanced Live2D VTuber Server on {host}:{actual_port}")
            logger.info(f"RAG System Status: {'Enabled' if self.rag_system else 'Disabled'}")
            
            try:
                uvicorn.run(
                    self.app,
                    host=host,
                    port=actual_port,
                    log_level=log_level,
                    access_log=True
                )
            except Exception as e:
                logger.error(f"Error starting server: {e}")
                raise
                
        except ImportError:
            logger.error("uvicorn is required to run the server. Install it with: pip install uvicorn")
            raise
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise

    @staticmethod
    def clean_cache():
        """Clean up any cached files"""
        cache_dir = "cache"
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)

    def clean_up(self):
        """Clean up resources"""
        cleanup_ports()


def load_config_with_env(path) -> dict:
    """
    Load configuration from YAML file with environment variable substitution
    """
    
    def replacer(match):
        env_var = match.group(1)
        default_value = match.group(2) if match.group(2) else ""
        return os.environ.get(env_var, default_value)
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace ${VAR} and ${VAR:default} patterns
        content = re.sub(r'\$\{([^}:]+)(?::([^}]*))?\}', replacer, content)
        
        config = yaml.safe_load(content)
        logger.info(f"Configuration loaded from {path} with environment substitution")
        return config
        
    except Exception as e:
        logger.error(f"Error loading config with environment substitution: {e}")
        return {}


# Enhanced model management classes
class ModelCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        self.cache[key] = value


class ModelManager:
    """Manager for ASR and TTS models with enhanced caching"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cache = ModelCache()
    
    def initialize_models(self) -> None:
        """Initialize ASR and TTS models"""
        self._init_asr()
        self._init_tts()
    
    def _init_asr(self) -> None:
        """Initialize ASR model"""
        # Implementation would go here
        pass
    
    def _init_tts(self) -> None:
        """Initialize TTS model"""
        # Implementation would go here
        pass
    
    def update_models(self, new_config: Dict) -> None:
        """Update ASR and TTS models based on new configuration"""
        try:
            if self._should_reinit_asr(new_config):
                self._update_asr()
            
            if self._should_reinit_tts(new_config):
                self._update_tts()
                
            self.config.update(new_config)
            logger.info("Models updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating models: {e}")
    
    def _should_reinit_asr(self, new_config: Dict) -> bool:
        """Check if ASR model should be reinitialized"""
        current_asr = self.config.get("ASR_MODEL")
        new_asr = new_config.get("ASR_MODEL")
        return current_asr != new_asr
    
    def _should_reinit_tts(self, new_config: Dict) -> bool:
        """Check if TTS model should be reinitialized"""
        current_tts = self.config.get("TTS_MODEL")
        new_tts = new_config.get("TTS_MODEL")
        return current_tts != new_tts
    
    def _update_asr(self) -> None:
        """Update ASR model"""
        # Implementation would go here
        pass
    
    def _update_tts(self) -> None:
        """Update TTS model"""
        # Implementation would go here
        pass


def _determine_object_category(response_text: str) -> str:
    """Determine object category from response text"""
    response_lower = response_text.lower()
    
    if any(word in response_lower for word in ['controller', 'gamepad', 'joystick']):
        return 'gaming_controller'
    elif any(word in response_lower for word in ['can', 'bottle', 'beverage', 'drink']):
        return 'beverage'
    elif any(word in response_lower for word in ['keyboard', 'mouse', 'computer']):
        return 'computer_peripheral'
    else:
        return 'unknown'


def _calculate_response_confidence(response_text: str) -> float:
    """Calculate confidence score for response"""
    # Simple heuristic based on response length and specificity
    if len(response_text) > 100:
        return 0.9
    elif len(response_text) > 50:
        return 0.7
    else:
        return 0.5


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced Live2D VTuber Server with AWS Knowledge Base RAG")
    parser.add_argument("--config", default="conf.yaml", help="Configuration file path")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    parser.add_argument("--log-level", default="info", help="Log level")
    parser.add_argument("--web", action="store_true", help="Enable web interface")
    
    args = parser.parse_args()
    
    # Load configuration with fallback
    config = load_config_with_env(args.config)
    
    # If config loading failed, provide default configuration
    if not config:
        logger.warning(f"Could not load config from {args.config}, using default configuration")
        config = {
            "LIVE2D_MODEL": "default",
            "LIVE2D": True,
            "TTS_ON": True,
            "VOICE_INPUT_ON": True,
            "LLM_PROVIDER": "claude",
            "ASR_MODEL": "Faster-Whisper",
            "TTS_MODEL": "EDGE_TTS",
            "VERBOSE": True,
            "SERVER_PORT": 8000,
            "WEBSOCKET_PORT": 8000,
            "MAX_TOKENS": 500,
            "SYSTEM_PROMPT": "You are a helpful AI assistant with RAG capabilities.",
            "PERSONA_CHOICE": "service_assistant",
            "LIVE2D_Expression_Prompt": "live2d_expression_prompt"
        }
    
    # Ensure required keys exist
    required_keys = {
        "LIVE2D_MODEL": "default",
        "LIVE2D": True,
        "TTS_ON": True,
        "VOICE_INPUT_ON": True
    }
    
    for key, default_value in required_keys.items():
        if key not in config:
            config[key] = default_value
            logger.info(f"Added missing config key {key} with default value: {default_value}")
    
    # Create and run server
    server = WebSocketServer(config, web=args.web)
    
    def signal_handler(signum, frame):
        logger.info("Shutting down server...")
        server.clean_up()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        server.run(host=args.host, port=args.port, log_level=args.log_level)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.clean_up()