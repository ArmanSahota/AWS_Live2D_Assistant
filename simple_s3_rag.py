#!/usr/bin/env python3
"""
Simple S3-Based RAG Implementation
==================================

This implements RAG using direct S3 document retrieval without OpenSearch.
Much simpler and cheaper than the full Bedrock Knowledge Base approach.
"""

import boto3
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib

@dataclass
class DocumentChunk:
    """A chunk of a document with metadata"""
    content: str
    source: str
    chunk_id: str
    relevance_score: float = 0.0

class SimpleS3RAG:
    """
    Simple RAG implementation that reads documents directly from S3
    and performs keyword-based retrieval without vector databases
    """
    
    def __init__(
        self, 
        bucket_name: str = "live2d-aws-backend-documentsbucket-gvqh2hzqj761",
        region: str = "us-west-2",
        document_prefix: str = "manufacturing/"
    ):
        self.bucket_name = bucket_name
        self.region = region
        self.document_prefix = document_prefix
        self.s3_client = boto3.client('s3', region_name=region)
        
        # Cache for documents to avoid repeated S3 calls
        self.document_cache = {}
        
        # Manufacturing-specific keywords for better matching
        self.manufacturing_keywords = {
            'safety': ['safety', 'lockout', 'tagout', 'emergency', 'ppe', 'hazard', 'warning'],
            'maintenance': ['maintenance', 'service', 'repair', 'lubricate', 'replace', 'inspect'],
            'troubleshooting': ['error', 'problem', 'fault', 'malfunction', 'broken', 'noise'],
            'parts': ['part', 'component', 'spare', 'replacement', 'catalog', 'number']
        }
    
    def load_documents_from_s3(self) -> Dict[str, str]:
        """Load all documents from S3 bucket"""
        try:
            print(f"📥 Loading documents from S3: {self.bucket_name}/{self.document_prefix}")
            
            # List objects in the manufacturing folder
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=self.document_prefix
            )
            
            documents = {}
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    key = obj['Key']
                    if key.endswith('.txt'):  # Only process text files
                        try:
                            # Download document content
                            doc_response = self.s3_client.get_object(
                                Bucket=self.bucket_name,
                                Key=key
                            )
                            content = doc_response['Body'].read().decode('utf-8')
                            documents[key] = content
                            print(f"✅ Loaded: {key}")
                        except Exception as e:
                            print(f"❌ Error loading {key}: {e}")
            
            self.document_cache = documents
            print(f"📚 Loaded {len(documents)} documents from S3")
            return documents
            
        except Exception as e:
            print(f"❌ Error loading documents from S3: {e}")
            return {}
    
    def chunk_document(self, content: str, source: str, chunk_size: int = 500) -> List[DocumentChunk]:
        """Split document into chunks for better retrieval"""
        chunks = []
        
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        chunk_num = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph would exceed chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunk_id = f"{source}_chunk_{chunk_num}"
                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    source=source,
                    chunk_id=chunk_id
                ))
                current_chunk = paragraph
                chunk_num += 1
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunk_id = f"{source}_chunk_{chunk_num}"
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                source=source,
                chunk_id=chunk_id
            ))
        
        return chunks
    
    def calculate_relevance_score(self, query: str, chunk: DocumentChunk) -> float:
        """Calculate relevance score using keyword matching and text similarity"""
        query_lower = query.lower()
        content_lower = chunk.content.lower()
        
        score = 0.0
        
        # Exact phrase matching (highest weight)
        query_phrases = [phrase.strip() for phrase in query_lower.split() if len(phrase.strip()) > 2]
        for phrase in query_phrases:
            if phrase in content_lower:
                score += 2.0
        
        # Manufacturing category matching
        for category, keywords in self.manufacturing_keywords.items():
            query_has_category = any(keyword in query_lower for keyword in keywords)
            content_has_category = any(keyword in content_lower for keyword in keywords)
            
            if query_has_category and content_has_category:
                score += 1.5
        
        # Individual word matching
        query_words = set(query_lower.split())
        content_words = set(content_lower.split())
        common_words = query_words.intersection(content_words)
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        meaningful_common_words = common_words - stop_words
        
        score += len(meaningful_common_words) * 0.5
        
        # Bonus for safety-related content
        safety_indicators = ['safety', 'warning', 'danger', 'caution', 'emergency']
        if any(indicator in query_lower for indicator in safety_indicators):
            if any(indicator in content_lower for indicator in safety_indicators):
                score += 2.0
        
        return score
    
    def retrieve_relevant_chunks(self, query: str, max_chunks: int = 3) -> List[DocumentChunk]:
        """Retrieve the most relevant document chunks for a query"""
        
        # Load documents if not cached
        if not self.document_cache:
            self.load_documents_from_s3()
        
        if not self.document_cache:
            print("❌ No documents available")
            return []
        
        # Create chunks from all documents
        all_chunks = []
        for source, content in self.document_cache.items():
            chunks = self.chunk_document(content, source)
            all_chunks.extend(chunks)
        
        # Calculate relevance scores
        for chunk in all_chunks:
            chunk.relevance_score = self.calculate_relevance_score(query, chunk)
        
        # Sort by relevance score and return top chunks
        relevant_chunks = sorted(all_chunks, key=lambda x: x.relevance_score, reverse=True)
        
        # Filter out chunks with very low scores
        filtered_chunks = [chunk for chunk in relevant_chunks if chunk.relevance_score > 0.5]
        
        return filtered_chunks[:max_chunks]
    
    def query(self, question: str) -> str:
        """Main query method that retrieves relevant content and formats response"""
        print(f"🔍 Processing query: {question}")
        
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(question, max_chunks=3)
        
        if not relevant_chunks:
            return """I don't have specific information about that in my manufacturing documents. 
            
I can help you with:
- Safety protocols like lockout/tagout procedures
- Emergency procedures and PPE requirements  
- Machine maintenance schedules
- Parts information and specifications

Could you try rephrasing your question or ask about one of these topics?"""
        
        # Format response with retrieved information
        response_parts = []
        response_parts.append("Based on the manufacturing documentation, here's what I found:")
        response_parts.append("")
        
        for i, chunk in enumerate(relevant_chunks, 1):
            source_name = chunk.source.split('/')[-1].replace('.txt', '').replace('-', ' ').title()
            response_parts.append(f"**From {source_name}:**")
            response_parts.append(chunk.content)
            response_parts.append("")
        
        # Add safety reminder for safety-related queries
        safety_keywords = ['safety', 'emergency', 'danger', 'warning', 'lockout', 'tagout']
        if any(keyword in question.lower() for keyword in safety_keywords):
            response_parts.append("⚠️ **Safety Reminder**: Always follow proper safety protocols and consult with qualified personnel for safety-critical procedures.")
        
        return "\n".join(response_parts)

def test_simple_s3_rag():
    """Test the Simple S3 RAG system"""
    print("🧪 Testing Simple S3 RAG System")
    print("=" * 50)
    
    # Initialize RAG system
    rag = SimpleS3RAG()
    
    # Test queries
    test_queries = [
        "What is the lockout tagout procedure?",
        "What PPE is required?",
        "Emergency procedures",
        "Machine maintenance schedule",
        "Part numbers and specifications"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        response = rag.query(query)
        print(response)
        print()

if __name__ == "__main__":
    test_simple_s3_rag()