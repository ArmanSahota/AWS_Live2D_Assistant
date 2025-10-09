"""
Vision + RAG Pipeline
Two-stage process: Vision analysis → RAG search → Enhanced response
"""

import boto3
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VisionAnalysis:
    """Result from vision analysis"""
    description: str
    objects_detected: List[str]
    manufacturing_relevance: str
    safety_concerns: List[str]
    technical_keywords: List[str]

@dataclass
class RAGContext:
    """RAG context retrieved based on vision analysis"""
    relevant_docs: List[Dict[str, Any]]
    search_query: str
    sources_used: int
    enhanced_context: str

class VisionRAGPipeline:
    """
    Two-stage Vision + RAG pipeline for manufacturing object analysis
    """
    
    def __init__(self, knowledge_base_id: str = "HVTKAK0Q86", region: str = "us-west-2"):
        """
        Initialize the Vision + RAG pipeline
        
        Args:
            knowledge_base_id: AWS Knowledge Base ID
            region: AWS region
        """
        self.knowledge_base_id = knowledge_base_id
        self.region = region
        
        # Initialize AWS clients
        try:
            self.bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
            self.bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=region)
            self.enabled = True
            logger.info(f"Vision RAG Pipeline initialized with KB: {knowledge_base_id}")
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
            self.enabled = False
    
    def analyze_image_with_claude(self, image_data: str, user_question: str = "") -> VisionAnalysis:
        """
        Stage 1: Analyze image with Claude Vision to extract manufacturing-relevant information
        
        Args:
            image_data: Base64 encoded image
            user_question: Optional user question about the image
            
        Returns:
            VisionAnalysis with extracted information
        """
        try:
            # Prepare vision analysis prompt
            vision_prompt = f"""Analyze this image and provide a detailed technical analysis focusing on:

1. OBJECT IDENTIFICATION: What specific objects, equipment, or components do you see?
2. MANUFACTURING RELEVANCE: How might this relate to manufacturing, maintenance, or industrial processes?
3. SAFETY CONCERNS: Are there any potential safety issues or hazards visible?
4. TECHNICAL KEYWORDS: What technical terms, part names, or error codes are relevant?
5. MAINTENANCE CONTEXT: Does this appear to be related to equipment maintenance, troubleshooting, or inspection?

User Question: {user_question}

Provide a structured analysis that can be used to search technical documentation."""

            # Prepare Claude Vision API call
            content = [
                {"type": "text", "text": vision_prompt},
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}}
            ]
            
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": content}],
                "temperature": 0.3
            }
            
            # Call Claude Vision using inference profile ARN
            model_id = "arn:aws:bedrock:us-west-2:615299772411:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
            response = self.bedrock_runtime.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            
            result = json.loads(response["body"].read())
            vision_text = result["content"][0]["text"]
            
            # Extract structured information from vision analysis
            vision_analysis = self._parse_vision_analysis(vision_text, user_question)
            
            logger.info(f"Vision analysis completed: {len(vision_analysis.technical_keywords)} keywords extracted")
            return vision_analysis
            
        except Exception as e:
            logger.error(f"Vision analysis failed: {e}")
            # Return fallback analysis
            return VisionAnalysis(
                description="Image analysis unavailable",
                objects_detected=[],
                manufacturing_relevance="Unknown",
                safety_concerns=[],
                technical_keywords=[]
            )
    
    def search_rag_with_vision_context(self, vision_analysis: VisionAnalysis, user_question: str = "") -> RAGContext:
        """
        Stage 2: Use vision analysis results to search RAG system for relevant context
        
        Args:
            vision_analysis: Results from vision analysis
            user_question: Original user question
            
        Returns:
            RAGContext with relevant documentation
        """
        try:
            # Build search query from vision analysis
            search_terms = []
            
            # Add detected objects
            search_terms.extend(vision_analysis.objects_detected)
            
            # Add technical keywords
            search_terms.extend(vision_analysis.technical_keywords)
            
            # Add manufacturing relevance
            if vision_analysis.manufacturing_relevance != "Unknown":
                search_terms.append(vision_analysis.manufacturing_relevance)
            
            # Add safety concerns
            search_terms.extend(vision_analysis.safety_concerns)
            
            # Add user question
            if user_question:
                search_terms.append(user_question)
            
            # Create comprehensive search query
            search_query = " ".join(search_terms)
            
            logger.info(f"RAG search query: {search_query[:100]}...")
            
            # Search Knowledge Base
            response = self.bedrock_agent.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={"text": search_query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": 5,
                        "overrideSearchType": "SEMANTIC"
                    }
                }
            )
            
            results = response.get("retrievalResults", [])
            
            # Format results
            relevant_docs = []
            for result in results:
                relevant_docs.append({
                    "content": result["content"]["text"],
                    "source": result["metadata"].get("source", "Unknown"),
                    "score": result.get("score", 0.0),
                    "location": result.get("location", {})
                })
            
            # Create enhanced context
            enhanced_context = self._create_enhanced_context(vision_analysis, relevant_docs, user_question)
            
            logger.info(f"RAG search completed: {len(relevant_docs)} documents found")
            
            return RAGContext(
                relevant_docs=relevant_docs,
                search_query=search_query,
                sources_used=len(relevant_docs),
                enhanced_context=enhanced_context
            )
            
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return RAGContext(
                relevant_docs=[],
                search_query="",
                sources_used=0,
                enhanced_context=""
            )
    
    def process_vision_with_rag(self, image_data: str, user_question: str = "") -> Dict[str, Any]:
        """
        Complete Vision + RAG pipeline
        
        Args:
            image_data: Base64 encoded image
            user_question: User's question about the image
            
        Returns:
            Complete analysis with vision + RAG context
        """
        if not self.enabled:
            return {
                "error": "Vision RAG pipeline not available",
                "vision_analysis": None,
                "rag_context": None,
                "enhanced_response": user_question
            }
        
        # Stage 1: Vision Analysis
        logger.info("Stage 1: Analyzing image with Claude Vision...")
        vision_analysis = self.analyze_image_with_claude(image_data, user_question)
        
        # Stage 2: RAG Search based on vision analysis
        logger.info("Stage 2: Searching RAG system with vision context...")
        rag_context = self.search_rag_with_vision_context(vision_analysis, user_question)
        
        # Stage 3: Create final enhanced response
        final_response = self._create_final_response(vision_analysis, rag_context, user_question)
        
        return {
            "vision_analysis": {
                "description": vision_analysis.description,
                "objects_detected": vision_analysis.objects_detected,
                "manufacturing_relevance": vision_analysis.manufacturing_relevance,
                "safety_concerns": vision_analysis.safety_concerns,
                "technical_keywords": vision_analysis.technical_keywords
            },
            "rag_context": {
                "sources_used": rag_context.sources_used,
                "search_query": rag_context.search_query,
                "relevant_docs": rag_context.relevant_docs[:3]  # Top 3 for response
            },
            "enhanced_response": final_response,
            "pipeline_success": True
        }
    
    def _parse_vision_analysis(self, vision_text: str, user_question: str) -> VisionAnalysis:
        """Parse Claude's vision analysis into structured data"""
        
        # Extract objects (simple keyword extraction)
        objects_detected = []
        manufacturing_terms = [
            "heater", "sensor", "motor", "pump", "valve", "conveyor", "machine", 
            "equipment", "control panel", "display", "gauge", "meter", "switch",
            "cable", "wire", "component", "part", "assembly", "tool"
        ]
        
        vision_lower = vision_text.lower()
        for term in manufacturing_terms:
            if term in vision_lower:
                objects_detected.append(term)
        
        # Extract safety concerns
        safety_keywords = ["warning", "danger", "caution", "hot", "electrical", "pressure", "hazard"]
        safety_concerns = []
        for keyword in safety_keywords:
            if keyword in vision_lower:
                safety_concerns.append(keyword)
        
        # Extract technical keywords
        technical_keywords = []
        if "error" in vision_lower or "fault" in vision_lower:
            technical_keywords.extend(["error", "troubleshooting", "fault"])
        if "maintenance" in vision_lower or "repair" in vision_lower:
            technical_keywords.extend(["maintenance", "repair", "service"])
        if "temperature" in vision_lower or "heat" in vision_lower:
            technical_keywords.extend(["temperature", "heating", "thermal"])
        
        # Determine manufacturing relevance
        manufacturing_relevance = "Unknown"
        if any(term in vision_lower for term in manufacturing_terms):
            manufacturing_relevance = "Industrial equipment or component"
        if "error" in vision_lower or "fault" in vision_lower:
            manufacturing_relevance = "Equipment troubleshooting"
        if "maintenance" in vision_lower:
            manufacturing_relevance = "Equipment maintenance"
        
        return VisionAnalysis(
            description=vision_text,
            objects_detected=objects_detected,
            manufacturing_relevance=manufacturing_relevance,
            safety_concerns=safety_concerns,
            technical_keywords=technical_keywords
        )
    
    def _create_enhanced_context(self, vision_analysis: VisionAnalysis, relevant_docs: List[Dict], user_question: str) -> str:
        """Create enhanced context combining vision and RAG results"""
        
        context_parts = []
        
        # Add vision analysis summary
        context_parts.append("=== VISION ANALYSIS ===")
        context_parts.append(f"Objects detected: {', '.join(vision_analysis.objects_detected) or 'None specific'}")
        context_parts.append(f"Manufacturing relevance: {vision_analysis.manufacturing_relevance}")
        
        if vision_analysis.safety_concerns:
            context_parts.append(f"⚠️ Safety concerns: {', '.join(vision_analysis.safety_concerns)}")
        
        context_parts.append("")
        
        # Add RAG documentation
        if relevant_docs:
            context_parts.append("=== RELEVANT DOCUMENTATION ===")
            for i, doc in enumerate(relevant_docs[:3], 1):
                safety_indicator = "⚠️ " if any(keyword in doc["content"].lower() 
                                             for keyword in ["safety", "warning", "danger", "caution"]) else ""
                context_parts.append(f"{i}. {safety_indicator}Source: {doc['source']} (Score: {doc['score']:.3f})")
                context_parts.append(f"   Content: {doc['content'][:400]}...")
                context_parts.append("")
            
            context_parts.append("=== END DOCUMENTATION ===")
        else:
            context_parts.append("=== NO RELEVANT DOCUMENTATION FOUND ===")
        
        context_parts.append("")
        context_parts.append(f"User Question: {user_question}")
        
        return "\n".join(context_parts)
    
    def _create_final_response(self, vision_analysis: VisionAnalysis, rag_context: RAGContext, user_question: str) -> str:
        """Create final enhanced response combining vision and RAG"""
        
        response_parts = []
        
        # Start with vision analysis
        if vision_analysis.objects_detected:
            objects_str = ", ".join(vision_analysis.objects_detected)
            response_parts.append(f"I can see {objects_str} in the image.")
        else:
            response_parts.append("I can see an object in the image.")
        
        # Add manufacturing context if relevant
        if vision_analysis.manufacturing_relevance != "Unknown":
            response_parts.append(f"This appears to be related to {vision_analysis.manufacturing_relevance.lower()}.")
        
        # Add safety warnings if detected
        if vision_analysis.safety_concerns:
            response_parts.append(f"⚠️ Safety note: I notice potential {', '.join(vision_analysis.safety_concerns)} concerns.")
        
        # Add RAG context if available
        if rag_context.sources_used > 0:
            response_parts.append(f"\nBased on our manufacturing documentation ({rag_context.sources_used} relevant documents found):")
            
            # Add key information from top document
            top_doc = rag_context.relevant_docs[0]
            key_info = top_doc["content"][:200]
            response_parts.append(f"• {key_info}...")
            
            if any("safety" in doc["content"].lower() for doc in rag_context.relevant_docs):
                response_parts.append("\n⚠️ Please follow all safety protocols when working with this equipment.")
        
        # Add helpful closing
        response_parts.append(f"\nWould you like me to provide more specific information about what I see or search for additional documentation?")
        
        return " ".join(response_parts)


# Integration function for existing server
def enhance_vision_analysis_with_rag(image_data: str, user_question: str = "", knowledge_base_id: str = "HVTKAK0Q86") -> Dict[str, Any]:
    """
    Enhanced vision analysis with RAG integration
    This function can be called from your existing server.py
    
    Args:
        image_data: Base64 encoded image
        user_question: User's question about the image
        knowledge_base_id: AWS Knowledge Base ID
        
    Returns:
        Enhanced analysis with vision + RAG context
    """
    try:
        # Initialize pipeline
        pipeline = VisionRAGPipeline(knowledge_base_id)
        
        # Process image with RAG enhancement
        result = pipeline.process_vision_with_rag(image_data, user_question)
        
        return result
        
    except Exception as e:
        logger.error(f"Vision RAG pipeline error: {e}")
        return {
            "error": str(e),
            "vision_analysis": None,
            "rag_context": None,
            "enhanced_response": "I can see an image, but I'm having trouble analyzing it with our documentation system."
        }


if __name__ == "__main__":
    # Test the Vision + RAG pipeline
    import base64
    from pathlib import Path
    
    # Test with a sample image (if available)
    test_images = [
        "Test_Photos/Keyboard.jpg",
        "Test_Photos/SodaPop.jpg", 
        "Test_Photos/SwitchController.jpg"
    ]
    
    for image_path in test_images:
        if Path(image_path).exists():
            print(f"\nTesting Vision + RAG pipeline with: {image_path}")
            
            # Load and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Test the pipeline
            result = enhance_vision_analysis_with_rag(
                image_data=image_data,
                user_question="What is this and how might it relate to manufacturing?",
                knowledge_base_id="HVTKAK0Q86"
            )
            
            print(f"Vision Analysis: {result.get('vision_analysis', {}).get('description', 'N/A')[:100]}...")
            print(f"RAG Sources: {result.get('rag_context', {}).get('sources_used', 0)}")
            print(f"Enhanced Response: {result.get('enhanced_response', 'N/A')[:200]}...")
            break
    else:
        print("No test images found. Pipeline is ready for integration.")