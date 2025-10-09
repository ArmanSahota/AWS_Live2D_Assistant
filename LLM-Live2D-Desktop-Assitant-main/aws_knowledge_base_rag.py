"""
AWS Knowledge Base RAG Integration
Enhanced RAG system using AWS Bedrock Knowledge Base for the Live2D VTuber Assistant
"""

import os
import json
import boto3
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RAGDocument:
    """Represents a document retrieved from AWS Knowledge Base"""
    content: str
    source: str
    score: float
    location: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class RAGResponse:
    """Response from RAG system with context and metadata"""
    enhanced_prompt: str
    documents: List[RAGDocument]
    sources_used: int
    retrieval_time: float
    knowledge_base_id: str
    query: str

class AWSKnowledgeBaseRAG:
    """
    AWS Knowledge Base RAG implementation for manufacturing assistant
    Integrates with existing Live2D VTuber system
    """
    
    def __init__(
        self,
        knowledge_base_id: str = None,
        region: str = "us-west-2",
        max_results: int = 5,
        score_threshold: float = 0.5
    ):
        """
        Initialize AWS Knowledge Base RAG client
        
        Args:
            knowledge_base_id: AWS Bedrock Knowledge Base ID
            region: AWS region
            max_results: Maximum number of documents to retrieve
            score_threshold: Minimum relevance score for documents
        """
        self.knowledge_base_id = knowledge_base_id or os.environ.get("AWS_KNOWLEDGE_BASE_ID")
        self.region = region
        self.max_results = max_results
        self.score_threshold = score_threshold
        
        if not self.knowledge_base_id:
            logger.warning("No Knowledge Base ID provided. RAG functionality will be disabled.")
            self.enabled = False
            return
        
        try:
            # Initialize AWS clients
            self.bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=region)
            self.s3_client = boto3.client("s3", region_name=region)
            self.enabled = True
            logger.info(f"AWS Knowledge Base RAG initialized with KB ID: {self.knowledge_base_id}")
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {e}")
            self.enabled = False
    
    def is_available(self) -> bool:
        """Check if RAG system is available"""
        return self.enabled and bool(self.knowledge_base_id)
    
    def retrieve_documents(
        self,
        query: str,
        search_type: str = "HYBRID",
        max_results: Optional[int] = None
    ) -> List[RAGDocument]:
        """
        Retrieve relevant documents from AWS Knowledge Base
        
        Args:
            query: Search query
            search_type: HYBRID, SEMANTIC, or KEYWORD
            max_results: Override default max results
            
        Returns:
            List of RAGDocument objects
        """
        if not self.is_available():
            logger.warning("AWS Knowledge Base RAG is not available")
            return []
        
        max_results = max_results or self.max_results
        
        try:
            start_time = datetime.now()
            
            response = self.bedrock_agent.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": max_results,
                        "overrideSearchType": search_type
                    }
                }
            )
            
            retrieval_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"Retrieved documents in {retrieval_time:.3f}s")
            
            documents = []
            for result in response.get("retrievalResults", []):
                score = result.get("score", 0.0)
                
                # Filter by score threshold
                if score < self.score_threshold:
                    continue
                
                doc = RAGDocument(
                    content=result["content"]["text"],
                    source=result["metadata"].get("source", "Unknown"),
                    score=score,
                    location=result.get("location", {}),
                    metadata=result.get("metadata", {})
                )
                documents.append(doc)
            
            logger.info(f"Retrieved {len(documents)} documents above threshold {self.score_threshold}")
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def enhance_prompt_with_context(
        self,
        query: str,
        documents: List[RAGDocument],
        context_template: str = None
    ) -> str:
        """
        Enhance user prompt with retrieved document context
        
        Args:
            query: Original user query
            documents: Retrieved documents
            context_template: Custom template for context formatting
            
        Returns:
            Enhanced prompt with context
        """
        if not documents:
            return query
        
        if context_template is None:
            context_template = self._get_default_context_template()
        
        # Build context from documents
        context_parts = ["=== RELEVANT MANUFACTURING DOCUMENTATION ===\n"]
        
        for i, doc in enumerate(documents, 1):
            # Add safety indicators
            safety_indicator = ""
            if any(keyword in doc.content.lower() for keyword in ["safety", "critical", "warning", "danger"]):
                safety_indicator = "⚠️ SAFETY-CRITICAL "
            
            context_parts.append(f"{i}. {safety_indicator}Source: {doc.source} (Relevance: {doc.score:.3f})")
            
            # Truncate content if too long
            content = doc.content
            if len(content) > 800:
                content = content[:800] + "... [Content truncated]"
            
            context_parts.append(f"   Content: {content}\n")
        
        context_parts.extend([
            "=== END DOCUMENTATION ===\n",
            "Instructions: Use the above documentation to provide accurate, detailed answers. ",
            "If the documentation contains safety information, emphasize safety protocols.\n",
            f"User Question: {query}"
        ])
        
        return "\n".join(context_parts)
    
    def get_rag_response(
        self,
        query: str,
        search_type: str = "HYBRID",
        include_metadata: bool = True
    ) -> RAGResponse:
        """
        Get complete RAG response with enhanced prompt and metadata
        
        Args:
            query: User query
            search_type: Search type for retrieval
            include_metadata: Whether to include retrieval metadata
            
        Returns:
            RAGResponse object with enhanced prompt and metadata
        """
        start_time = datetime.now()
        
        # Retrieve documents
        documents = self.retrieve_documents(query, search_type)
        
        # Enhance prompt
        enhanced_prompt = self.enhance_prompt_with_context(query, documents)
        
        retrieval_time = (datetime.now() - start_time).total_seconds()
        
        return RAGResponse(
            enhanced_prompt=enhanced_prompt,
            documents=documents,
            sources_used=len(documents),
            retrieval_time=retrieval_time,
            knowledge_base_id=self.knowledge_base_id,
            query=query
        )
    
    def _get_default_context_template(self) -> str:
        """Get default context template for manufacturing assistant"""
        return """
You are a manufacturing assistant with access to technical documentation.
Use the provided documentation to give accurate, detailed answers.
Always prioritize safety and follow established protocols.
If you're unsure about something, say so and recommend consulting additional resources.
"""
    
    def get_document_sources(self) -> List[Dict[str, Any]]:
        """
        Get list of available document sources in the knowledge base
        Note: This requires additional AWS API calls and may not be available in all setups
        """
        try:
            # This would require additional setup to track document sources
            # For now, return empty list
            logger.info("Document source listing not implemented yet")
            return []
        except Exception as e:
            logger.error(f"Error getting document sources: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the RAG system
        
        Returns:
            Health status dictionary
        """
        status = {
            "enabled": self.enabled,
            "knowledge_base_id": self.knowledge_base_id,
            "region": self.region,
            "max_results": self.max_results,
            "score_threshold": self.score_threshold,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.enabled:
            try:
                # Test retrieval with a simple query
                test_docs = self.retrieve_documents("test query", max_results=1)
                status["test_retrieval"] = "success"
                status["test_documents_found"] = len(test_docs)
            except Exception as e:
                status["test_retrieval"] = "failed"
                status["error"] = str(e)
        
        return status


class HybridRAGSystem:
    """
    Hybrid RAG system that combines AWS Knowledge Base with local RAG
    Provides fallback and redundancy for better reliability
    """
    
    def __init__(
        self,
        aws_kb_id: str = None,
        local_rag_client = None,
        prefer_aws: bool = True
    ):
        """
        Initialize hybrid RAG system
        
        Args:
            aws_kb_id: AWS Knowledge Base ID
            local_rag_client: Local RAG client (e.g., SimpleS3RAG)
            prefer_aws: Whether to prefer AWS KB over local RAG
        """
        self.aws_rag = AWSKnowledgeBaseRAG(aws_kb_id) if aws_kb_id else None
        self.local_rag = local_rag_client
        self.prefer_aws = prefer_aws
        
        logger.info(f"Hybrid RAG initialized - AWS: {bool(self.aws_rag and self.aws_rag.is_available())}, Local: {bool(self.local_rag)}")
    
    def get_context(self, query: str, max_results: int = 5) -> RAGResponse:
        """
        Get RAG context using hybrid approach
        
        Args:
            query: User query
            max_results: Maximum results to return
            
        Returns:
            RAGResponse with best available context
        """
        # Try AWS Knowledge Base first if preferred and available
        if self.prefer_aws and self.aws_rag and self.aws_rag.is_available():
            try:
                response = self.aws_rag.get_rag_response(query)
                if response.sources_used > 0:
                    logger.info(f"Using AWS Knowledge Base - found {response.sources_used} documents")
                    return response
                else:
                    logger.info("AWS Knowledge Base returned no results, trying local RAG")
            except Exception as e:
                logger.warning(f"AWS Knowledge Base failed, falling back to local RAG: {e}")
        
        # Fallback to local RAG
        if self.local_rag:
            try:
                # Adapt local RAG response to RAGResponse format
                local_response = self.local_rag.get_context(query)
                
                # Convert to RAGResponse format
                documents = []
                if hasattr(local_response, 'relevant_docs') and local_response.relevant_docs:
                    for doc in local_response.relevant_docs[:max_results]:
                        documents.append(RAGDocument(
                            content=doc.get('content', ''),
                            source=doc.get('source', 'Local'),
                            score=doc.get('score', 0.8),
                            location={},
                            metadata=doc
                        ))
                
                enhanced_prompt = query
                if documents:
                    enhanced_prompt = self._format_local_context(query, documents)
                
                logger.info(f"Using local RAG - found {len(documents)} documents")
                return RAGResponse(
                    enhanced_prompt=enhanced_prompt,
                    documents=documents,
                    sources_used=len(documents),
                    retrieval_time=0.0,
                    knowledge_base_id="local",
                    query=query
                )
                
            except Exception as e:
                logger.error(f"Local RAG also failed: {e}")
        
        # No RAG available, return original query
        logger.warning("No RAG systems available, returning original query")
        return RAGResponse(
            enhanced_prompt=query,
            documents=[],
            sources_used=0,
            retrieval_time=0.0,
            knowledge_base_id="none",
            query=query
        )
    
    def _format_local_context(self, query: str, documents: List[RAGDocument]) -> str:
        """Format local RAG context similar to AWS format"""
        if not documents:
            return query
        
        context_parts = ["=== LOCAL MANUFACTURING DOCUMENTATION ===\n"]
        
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"{i}. Source: {doc.source}")
            context_parts.append(f"   Content: {doc.content[:800]}...\n")
        
        context_parts.extend([
            "=== END DOCUMENTATION ===\n",
            f"User Question: {query}"
        ])
        
        return "\n".join(context_parts)
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for hybrid system"""
        status = {
            "hybrid_rag": True,
            "prefer_aws": self.prefer_aws,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.aws_rag:
            status["aws_rag"] = self.aws_rag.health_check()
        else:
            status["aws_rag"] = {"enabled": False}
        
        if self.local_rag:
            status["local_rag"] = {"enabled": True, "type": type(self.local_rag).__name__}
        else:
            status["local_rag"] = {"enabled": False}
        
        return status


# Utility functions for integration with existing server.py
def create_rag_system(config: dict = None) -> HybridRAGSystem:
    """
    Factory function to create RAG system based on configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured HybridRAGSystem
    """
    config = config or {}
    
    # Get AWS Knowledge Base ID from config or environment
    aws_kb_id = config.get('AWS_KNOWLEDGE_BASE_ID') or os.environ.get('AWS_KNOWLEDGE_BASE_ID')
    
    # Try to import and create local RAG client
    local_rag = None
    try:
        from simple_s3_rag import SimpleS3RAG
        
        # Create a wrapper to match the expected interface
        class SimpleS3RAGWrapper:
            def __init__(self):
                self.s3_rag = SimpleS3RAG()
            
            def get_context(self, query: str):
                """Wrapper to match expected interface"""
                try:
                    # Try different method names that might exist
                    if hasattr(self.s3_rag, 'search_documents'):
                        docs = self.s3_rag.search_documents(query)
                    elif hasattr(self.s3_rag, 'get_relevant_documents'):
                        docs = self.s3_rag.get_relevant_documents(query)
                    elif hasattr(self.s3_rag, 'query'):
                        docs = self.s3_rag.query(query)
                    else:
                        # Fallback: return empty result
                        docs = []
                    
                    # Create a mock response object
                    class MockResponse:
                        def __init__(self, docs):
                            self.relevant_docs = docs if isinstance(docs, list) else []
                    
                    return MockResponse(docs)
                except Exception as e:
                    logger.error(f"SimpleS3RAG wrapper error: {e}")
                    class MockResponse:
                        def __init__(self):
                            self.relevant_docs = []
                    return MockResponse()
        
        local_rag = SimpleS3RAGWrapper()
        logger.info("Local S3 RAG client created with wrapper")
    except ImportError:
        logger.info("Local S3 RAG not available")
    except Exception as e:
        logger.warning(f"Failed to create local RAG client: {e}")
    
    # Create hybrid system
    return HybridRAGSystem(
        aws_kb_id=aws_kb_id,
        local_rag_client=local_rag,
        prefer_aws=config.get('PREFER_AWS_RAG', True)
    )


def enhance_server_with_aws_rag(server_instance):
    """
    Enhance existing server.py with AWS Knowledge Base RAG
    This function can be called to add RAG capabilities to the existing server
    """
    try:
        # Create RAG system
        rag_system = create_rag_system()
        
        # Add RAG system to server instance
        server_instance.rag_system = rag_system
        
        logger.info("Server enhanced with AWS Knowledge Base RAG")
        return True
        
    except Exception as e:
        logger.error(f"Failed to enhance server with AWS RAG: {e}")
        return False


if __name__ == "__main__":
    # Test the AWS Knowledge Base RAG system
    import asyncio
    
    async def test_rag():
        # Initialize RAG system
        rag = AWSKnowledgeBaseRAG()
        
        if not rag.is_available():
            print("AWS Knowledge Base RAG is not available. Check configuration.")
            return
        
        # Test health check
        health = rag.health_check()
        print(f"Health check: {json.dumps(health, indent=2)}")
        
        # Test retrieval
        test_query = "manufacturing error troubleshooting"
        print(f"\nTesting query: '{test_query}'")
        
        response = rag.get_rag_response(test_query)
        print(f"Found {response.sources_used} documents in {response.retrieval_time:.3f}s")
        
        for i, doc in enumerate(response.documents, 1):
            print(f"{i}. {doc.source} (score: {doc.score:.3f})")
            print(f"   {doc.content[:100]}...")
        
        print(f"\nEnhanced prompt length: {len(response.enhanced_prompt)} characters")
    
    asyncio.run(test_rag())