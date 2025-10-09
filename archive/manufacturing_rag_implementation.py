"""
Manufacturing RAG Implementation Example
========================================

This module demonstrates how to integrate AWS RAG capabilities into the existing
VTuber assistant for manufacturing environments. It extends the current Claude
client with manufacturing-specific knowledge retrieval and processing.

Based on the existing architecture in LLM-Live2D-Desktop-Assistant-main/
"""

import json
import asyncio
import boto3
import base64
from typing import Iterator, Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import hashlib

# Import from existing codebase - create a simple interface if not available
try:
    from llm.llm_interface import LLMInterface
except ImportError:
    # Create a simple base interface if the original doesn't exist
    class LLMInterface:
        def __init__(self):
            pass
        
        def chat_iter(self, prompt: str, image_base64=None):
            """Base chat iteration method"""
            yield "Base LLM interface response"
        
        def handle_interrupt(self, heard_response: str) -> None:
            """Handle interruption"""
            pass


@dataclass
class ManufacturingContext:
    """Context information for manufacturing queries"""
    machine_id: Optional[str] = None
    error_code: Optional[str] = None
    department: Optional[str] = None
    shift: Optional[str] = None
    operator_id: Optional[str] = None
    safety_level: Optional[str] = None


@dataclass
class RetrievedDocument:
    """Structure for retrieved manufacturing documents"""
    content: str
    title: str
    source: str
    confidence_score: float
    document_type: str
    safety_level: str
    machine_models: List[str]
    last_updated: datetime


class ManufacturingDocumentProcessor:
    """
    Processes and categorizes manufacturing documents for optimal retrieval
    """
    
    def __init__(self, s3_bucket: str, region: str = 'us-east-1'):
        self.s3_bucket = s3_bucket
        self.s3_client = boto3.client('s3', region_name=region)
        
        # Manufacturing document categories
        self.document_types = {
            'manual': ['manual', 'handbook', 'guide', 'instruction'],
            'schematic': ['schematic', 'diagram', 'blueprint', 'drawing'],
            'safety': ['safety', 'hazard', 'warning', 'protocol', 'procedure'],
            'troubleshooting': ['troubleshoot', 'diagnostic', 'repair', 'maintenance'],
            'parts': ['parts', 'catalog', 'inventory', 'component', 'spare']
        }
        
        # Safety level keywords
        self.safety_levels = {
            'critical': ['danger', 'critical', 'fatal', 'emergency', 'lockout'],
            'high': ['warning', 'caution', 'hazard', 'risk'],
            'medium': ['notice', 'attention', 'important'],
            'low': ['note', 'tip', 'information']
        }
    
    def extract_manufacturing_metadata(self, document_content: str, filename: str) -> Dict[str, Any]:
        """
        Extract manufacturing-specific metadata from document content
        """
        content_lower = document_content.lower()
        
        # Extract machine models (common patterns)
        machine_models = []
        machine_patterns = [
            r'model\s+([A-Z0-9\-]+)',
            r'machine\s+([A-Z0-9\-]+)',
            r'equipment\s+([A-Z0-9\-]+)',
            r'part\s+number\s+([A-Z0-9\-]+)'
        ]
        
        for pattern in machine_patterns:
            matches = re.findall(pattern, document_content, re.IGNORECASE)
            machine_models.extend(matches)
        
        # Determine document type
        document_type = 'general'
        for doc_type, keywords in self.document_types.items():
            if any(keyword in content_lower or keyword in filename.lower() for keyword in keywords):
                document_type = doc_type
                break
        
        # Determine safety level
        safety_level = 'low'
        for level, keywords in self.safety_levels.items():
            if any(keyword in content_lower for keyword in keywords):
                safety_level = level
                break
        
        # Extract department information
        departments = ['production', 'maintenance', 'quality', 'safety', 'engineering']
        department = None
        for dept in departments:
            if dept in content_lower or dept in filename.lower():
                department = dept
                break
        
        return {
            'document_type': document_type,
            'safety_level': safety_level,
            'machine_models': list(set(machine_models)),
            'department': department,
            'filename': filename,
            'content_length': len(document_content),
            'last_processed': datetime.now().isoformat()
        }


class ManufacturingQueryProcessor:
    """
    Processes manufacturing queries with domain-specific enhancements
    """
    
    def __init__(self, bedrock_client, knowledge_base_id: str):
        self.bedrock_client = bedrock_client
        self.knowledge_base_id = knowledge_base_id
        
        # Manufacturing-specific query patterns
        self.query_patterns = {
            'emergency': ['emergency', 'stop', 'shutdown', 'danger', 'accident'],
            'troubleshooting': ['error', 'problem', 'fault', 'malfunction', 'broken'],
            'maintenance': ['maintenance', 'service', 'repair', 'replace', 'check'],
            'parts': ['part', 'component', 'spare', 'replacement', 'catalog'],
            'safety': ['safety', 'hazard', 'warning', 'protocol', 'procedure']
        }
    
    def classify_query_intent(self, query: str) -> str:
        """
        Classify the intent of a manufacturing query
        """
        query_lower = query.lower()
        
        for intent, keywords in self.query_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        return 'general'
    
    def enhance_query_with_context(self, query: str, context: ManufacturingContext) -> str:
        """
        Enhance query with manufacturing context for better retrieval
        """
        enhancements = []
        
        if context.machine_id:
            enhancements.append(f"Machine: {context.machine_id}")
        
        if context.error_code:
            enhancements.append(f"Error Code: {context.error_code}")
            
        if context.department:
            enhancements.append(f"Department: {context.department}")
            
        if context.safety_level:
            enhancements.append(f"Safety Level: {context.safety_level}")
        
        enhanced_query = query
        if enhancements:
            enhanced_query = f"{query}\n\nContext: {', '.join(enhancements)}"
            
        return enhanced_query
    
    async def retrieve_manufacturing_documents(self, query: str, context: ManufacturingContext = None) -> List[RetrievedDocument]:
        """
        Retrieve relevant manufacturing documents using AWS Bedrock Knowledge Base
        """
        try:
            # Enhance query with context
            if context:
                enhanced_query = self.enhance_query_with_context(query, context)
            else:
                enhanced_query = query
            
            # Classify query intent for better filtering
            query_intent = self.classify_query_intent(query)
            
            # Retrieve from Bedrock Knowledge Base
            response = await asyncio.to_thread(
                self.bedrock_client.retrieve,
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={'text': enhanced_query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 10,
                        'overrideSearchType': 'HYBRID'  # Combine semantic and keyword search
                    }
                }
            )
            
            # Process and filter results
            retrieved_docs = []
            for result in response.get('retrievalResults', []):
                doc = RetrievedDocument(
                    content=result['content']['text'],
                    title=result['metadata'].get('title', 'Unknown'),
                    source=result['metadata'].get('source', 'Unknown'),
                    confidence_score=result['score'],
                    document_type=result['metadata'].get('document_type', 'general'),
                    safety_level=result['metadata'].get('safety_level', 'low'),
                    machine_models=result['metadata'].get('machine_models', []),
                    last_updated=datetime.fromisoformat(
                        result['metadata'].get('last_updated', datetime.now().isoformat())
                    )
                )
                retrieved_docs.append(doc)
            
            # Filter by context if provided
            if context:
                retrieved_docs = self.filter_by_context(retrieved_docs, context)
            
            # Sort by relevance and safety level
            retrieved_docs.sort(key=lambda x: (
                x.safety_level == 'critical',  # Critical safety docs first
                x.confidence_score
            ), reverse=True)
            
            return retrieved_docs[:5]  # Return top 5 most relevant
            
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
    
    def filter_by_context(self, docs: List[RetrievedDocument], context: ManufacturingContext) -> List[RetrievedDocument]:
        """
        Filter retrieved documents based on manufacturing context
        """
        filtered_docs = []
        
        for doc in docs:
            # Filter by machine ID if specified
            if context.machine_id:
                if context.machine_id in doc.machine_models or not doc.machine_models:
                    filtered_docs.append(doc)
            else:
                filtered_docs.append(doc)
        
        return filtered_docs


class ManufacturingRAGClient(LLMInterface):
    """
    Enhanced Claude client with RAG capabilities for manufacturing environments
    
    Extends the existing LLM interface with manufacturing-specific features:
    - Document retrieval from AWS Bedrock Knowledge Base
    - Manufacturing context awareness
    - Safety-first response generation
    - Technical documentation integration
    """
    
    def __init__(
        self,
        system: str = None,
        base_url: str = None,
        model: str = "claude-3-haiku-20240307",
        knowledge_base_id: str = None,
        aws_region: str = 'us-west-2',
        documents_bucket_name: str = 'live2d-aws-backend-documentsbucket-gvqh2hzqj761',
        verbose: bool = False,
    ):
        super().__init__()
        self.system = system or self.get_manufacturing_system_prompt()
        self.base_url = base_url or 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev'
        self.model = model
        self.verbose = verbose
        self.knowledge_base_id = knowledge_base_id
        self.aws_region = aws_region
        self.documents_bucket_name = documents_bucket_name
        
        # Initialize AWS clients
        self.bedrock_client = boto3.client('bedrock-agent-runtime', region_name=aws_region)
        
        # Initialize document processor
        self.document_processor = ManufacturingDocumentProcessor(
            s3_bucket=documents_bucket_name,
            region=aws_region
        )
        
        # Initialize query processor
        self.query_processor = ManufacturingQueryProcessor(
            bedrock_client=self.bedrock_client,
            knowledge_base_id=knowledge_base_id
        )
        
        # Cache for frequently accessed information
        self.response_cache = {}
        
        # Store conversation history
        self.messages = []
        
        if self.verbose:
            print(f"Initialized Manufacturing RAG Client:")
            print(f"  - Base URL: {self.base_url}")
            print(f"  - AWS Region: {aws_region}")
            print(f"  - Documents Bucket: {documents_bucket_name}")
            print(f"  - Knowledge Base: {knowledge_base_id or 'Not configured'}")
    
    def get_manufacturing_system_prompt(self) -> str:
        """
        Manufacturing-specific system prompt for Claude
        """
        return """You are a specialized manufacturing assistant with access to technical documentation, 
        machine manuals, safety protocols, and troubleshooting guides. Your responses must:

        1. 🚨 PRIORITIZE SAFETY: Always highlight safety warnings and precautions first
        2. 📋 BE PRECISE: Provide exact part numbers, specifications, and procedures
        3. 📖 CITE SOURCES: Reference the specific manual or document for each piece of information
        4. 🗣️ USE CLEAR LANGUAGE: Avoid unnecessary jargon, explain technical terms when needed
        5. 📝 PROVIDE STEP-BY-STEP GUIDANCE: Break complex procedures into numbered steps
        6. ⚠️ HIGHLIGHT CRITICAL INFORMATION: Use emphasis for important warnings or specifications
        7. 🔍 BE THOROUGH: Include relevant context like part numbers, model compatibility, and prerequisites

        When you don't have specific information in the retrieved context, clearly state this 
        and recommend consulting the appropriate manual or contacting a qualified technician.

        Format your responses for voice output - avoid complex formatting that would be difficult to speak aloud.
        Use natural speech patterns and clear transitions between topics."""
    
    def generate_cache_key(self, prompt: str, context: ManufacturingContext = None) -> str:
        """
        Generate cache key for manufacturing queries
        """
        context_str = ""
        if context:
            context_str = f"{context.machine_id}_{context.error_code}_{context.department}"
        
        combined = f"{prompt}_{context_str}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    async def chat_iter_with_rag(
        self, 
        prompt: str, 
        image_base64: str = None, 
        context: ManufacturingContext = None
    ) -> Iterator[str]:
        """
        Enhanced chat with RAG integration for manufacturing queries
        """
        try:
            # Check cache first for common queries
            cache_key = self.generate_cache_key(prompt, context)
            if cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                if self.verbose:
                    print(f"[MANUFACTURING RAG] Using cached response for query")
                for char in cached_response:
                    yield char
                return
            
            # Retrieve relevant manufacturing documents
            if self.verbose:
                print(f"[MANUFACTURING RAG] Retrieving documents for: {prompt[:100]}...")
            
            retrieved_docs = await self.query_processor.retrieve_manufacturing_documents(
                prompt, context
            )
            
            if self.verbose:
                print(f"[MANUFACTURING RAG] Retrieved {len(retrieved_docs)} relevant documents")
            
            # Construct enhanced prompt with retrieved context
            enhanced_prompt = self.construct_manufacturing_prompt(
                original_prompt=prompt,
                retrieved_docs=retrieved_docs,
                context=context
            )
            
            # Prepare payload for Claude API
            payload = {
                "text": enhanced_prompt,
                "system": self.system,
                "retrieved_context": [
                    {
                        "title": doc.title,
                        "source": doc.source,
                        "content": doc.content[:1000],  # Limit content length
                        "safety_level": doc.safety_level
                    }
                    for doc in retrieved_docs
                ]
            }
            
            # Add image if provided
            if image_base64:
                payload["image"] = image_base64
                payload["has_vision"] = True
                if self.verbose:
                    print(f"[MANUFACTURING RAG] Including image analysis")
            
            # Add conversation history
            if self.messages:
                payload["messages"] = self.messages[-4:]  # Keep last 4 messages for context
            
            # Send request to Claude API (using existing HTTP endpoint)
            import requests
            
            if not self.base_url:
                error_msg = "AWS base URL not configured for manufacturing RAG client"
                yield error_msg
                return
            
            response = requests.post(
                f"{self.base_url}/claude",
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                error_msg = f"HTTP error {response.status_code}: {response.text}"
                yield error_msg
                return
            
            data = response.json()
            if "reply" not in data:
                error_msg = "Invalid response format: missing 'reply' field"
                yield error_msg
                return
            
            response_text = data["reply"]
            
            # Cache the response for future use
            self.response_cache[cache_key] = response_text
            
            # Add safety warnings if high-risk content detected
            if any(doc.safety_level in ['critical', 'high'] for doc in retrieved_docs):
                safety_prefix = "⚠️ SAFETY NOTICE: This response contains safety-critical information. Please follow all safety protocols. "
                response_text = safety_prefix + response_text
            
            # Stream the response
            for char in response_text:
                yield char
            
            # Update conversation history
            self.messages.append({"role": "user", "content": prompt})
            self.messages.append({"role": "assistant", "content": response_text})
            
            # Keep conversation history manageable
            if len(self.messages) > 10:
                self.messages = self.messages[-8:]
            
            if self.verbose:
                print(f"[MANUFACTURING RAG] Response generated successfully ({len(response_text)} chars)")
                
        except Exception as e:
            error_msg = f"Error in manufacturing RAG chat: {str(e)}"
            if self.verbose:
                print(f"[MANUFACTURING RAG] {error_msg}")
            yield error_msg
    
    def construct_manufacturing_prompt(
        self, 
        original_prompt: str, 
        retrieved_docs: List[RetrievedDocument],
        context: ManufacturingContext = None
    ) -> str:
        """
        Construct enhanced prompt with retrieved manufacturing context
        """
        sections = []
        
        # Add context information if available
        if context:
            context_info = []
            if context.machine_id:
                context_info.append(f"Machine: {context.machine_id}")
            if context.error_code:
                context_info.append(f"Error Code: {context.error_code}")
            if context.department:
                context_info.append(f"Department: {context.department}")
            if context.operator_id:
                context_info.append(f"Operator: {context.operator_id}")
            
            if context_info:
                sections.append("🏭 MANUFACTURING CONTEXT:")
                sections.append(", ".join(context_info))
                sections.append("")
        
        # Add safety warnings first (highest priority)
        safety_docs = [doc for doc in retrieved_docs if doc.safety_level in ['critical', 'high']]
        if safety_docs:
            sections.append("🚨 SAFETY-CRITICAL INFORMATION:")
            for doc in safety_docs:
                sections.append(f"⚠️ {doc.title} (Source: {doc.source})")
                sections.append(f"   {doc.content[:300]}...")
                sections.append("")
        
        # Add technical documentation
        technical_docs = [doc for doc in retrieved_docs if doc.safety_level not in ['critical', 'high']]
        if technical_docs:
            sections.append("📋 RELEVANT TECHNICAL DOCUMENTATION:")
            for i, doc in enumerate(technical_docs, 1):
                sections.append(f"{i}. {doc.title}")
                sections.append(f"   Source: {doc.source}")
                sections.append(f"   Machine Models: {', '.join(doc.machine_models) if doc.machine_models else 'General'}")
                sections.append(f"   Content: {doc.content[:400]}...")
                sections.append("")
        
        # Add original user question
        sections.append("❓ USER QUESTION:")
        sections.append(original_prompt)
        
        return "\n".join(sections)
    
    def chat_iter(self, prompt: str, image_base64=None) -> Iterator[str]:
        """
        Standard chat interface - delegates to RAG-enhanced version
        """
        # Run async method in sync context
        import asyncio
        
        async def async_chat():
            result = []
            async for token in self.chat_iter_with_rag(prompt, image_base64):
                result.append(token)
            return "".join(result)
        
        try:
            # Get or create event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(async_chat())
        
        # Yield character by character to maintain streaming interface
        for char in response:
            yield char
    
    def handle_interrupt(self, heard_response: str) -> None:
        """
        Handle interruption by updating the last assistant message
        """
        if self.messages and self.messages[-1]["role"] == "assistant":
            self.messages[-1]["content"] = heard_response


# Example usage and integration helper
class ManufacturingAssistantIntegration:
    """
    Helper class to integrate manufacturing RAG capabilities into existing VTuber assistant
    """
    
    @staticmethod
    def create_manufacturing_client(config: dict) -> ManufacturingRAGClient:
        """
        Create a manufacturing RAG client from existing configuration
        """
        return ManufacturingRAGClient(
            base_url=config.get('HTTP_BASE_URL'),
            knowledge_base_id=config.get('MANUFACTURING_KB_ID'),
            aws_region=config.get('AWS_REGION', 'us-east-1'),
            verbose=config.get('VERBOSE', False)
        )
    
    @staticmethod
    def extract_manufacturing_context_from_voice(transcript: str) -> ManufacturingContext:
        """
        Extract manufacturing context from voice input
        """
        context = ManufacturingContext()
        
        # Extract machine ID patterns
        machine_patterns = [
            r'machine\s+([A-Z0-9\-]+)',
            r'equipment\s+([A-Z0-9\-]+)',
            r'unit\s+([A-Z0-9\-]+)'
        ]
        
        for pattern in machine_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                context.machine_id = match.group(1)
                break
        
        # Extract error codes
        error_patterns = [
            r'error\s+([A-Z0-9\-]+)',
            r'code\s+([A-Z0-9\-]+)',
            r'fault\s+([A-Z0-9\-]+)'
        ]
        
        for pattern in error_patterns:
            match = re.search(pattern, transcript, re.IGNORECASE)
            if match:
                context.error_code = match.group(1)
                break
        
        # Extract department
        departments = ['production', 'maintenance', 'quality', 'safety', 'engineering']
        for dept in departments:
            if dept in transcript.lower():
                context.department = dept
                break
        
        return context


# Configuration example for integration
MANUFACTURING_CONFIG_EXAMPLE = {
    'HTTP_BASE_URL': 'https://your-aws-api-gateway-url.com',
    'MANUFACTURING_KB_ID': 'your-bedrock-knowledge-base-id',
    'AWS_REGION': 'us-east-1',
    'VERBOSE': True,
    'CACHE_SIZE': 100,
    'SAFETY_PRIORITY': True
}

if __name__ == "__main__":
    # Example usage
    print("Manufacturing RAG Implementation Example")
    print("This module demonstrates RAG integration for manufacturing environments")
    print("Configure your AWS credentials and Knowledge Base ID to use this implementation")