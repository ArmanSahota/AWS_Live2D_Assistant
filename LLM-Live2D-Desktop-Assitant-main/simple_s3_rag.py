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
        
        # Check for specific error codes first
        error_code_match = re.search(r'error\s+code\s+([A-Z0-9]+)|code\s+([A-Z0-9]+)', question, re.IGNORECASE)
        if error_code_match:
            error_code = error_code_match.group(1) or error_code_match.group(2)
            return self._handle_error_code_query(question, error_code)
        
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(question, max_chunks=3)
        
        # Check if we have truly relevant content
        if not relevant_chunks or not self._has_specific_relevant_content(question, relevant_chunks):
            return self._generate_intelligent_fallback(question)
        
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
    
    def _handle_error_code_query(self, question: str, error_code: str) -> str:
        """Handle specific error code queries intelligently"""
        # Load documents if not cached
        if not self.document_cache:
            self.load_documents_from_s3()
        
        # Search for the specific error code in documents
        for source, content in self.document_cache.items():
            if error_code.upper() in content.upper():
                # Extract the section about this specific error code
                lines = content.split('\n')
                error_section = []
                capturing = False
                
                for line in lines:
                    if error_code.upper() in line.upper():
                        capturing = True
                        error_section.append(line)
                    elif capturing:
                        if line.strip() == "" or line.startswith("Error Code") or line.startswith("**"):
                            if line.strip() != "":
                                break
                        error_section.append(line)
                
                if error_section:
                    source_name = source.split('/')[-1].replace('.txt', '').replace('-', ' ').title()
                    return f"Based on the manufacturing documentation, here's what I found:\n\n**From {source_name}:**\n" + "\n".join(error_section)
        
        # Error code not found - provide intelligent response
        return f"""I don't have specific information about error code {error_code} in my current manufacturing documentation.

For unknown error codes, I recommend:
1. **Check your equipment manual** - Look for the error code section specific to your machine
2. **Contact the equipment manufacturer** - They have the most up-to-date error code definitions
3. **Document the symptoms** - Note what was happening when the error occurred
4. **Contact maintenance** - Extension 2345 for immediate assistance

I do have information about common error codes E001 (Spindle Overload) and E002 (Axis Drive Fault) if those would be helpful."""
    
    def _has_specific_relevant_content(self, question: str, chunks: List[DocumentChunk]) -> bool:
        """Check if the retrieved chunks actually contain specific relevant information"""
        question_lower = question.lower()
        
        # For equipment-specific queries, check if we have specific equipment info
        equipment_terms = ['machine', 'equipment', 'device', 'system', 'unit']
        if any(term in question_lower for term in equipment_terms):
            # Check if any chunk specifically mentions the equipment asked about
            for chunk in chunks:
                chunk_lower = chunk.content.lower()
                # Look for specific equipment names or models in the question
                question_words = set(question_lower.split())
                chunk_words = set(chunk_lower.split())
                
                # If there's significant overlap beyond generic terms, it's relevant
                meaningful_overlap = question_words.intersection(chunk_words) - {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'machine', 'equipment', 'error', 'code'}
                if len(meaningful_overlap) >= 2:
                    return True
            return False
        
        # For other queries, if we have chunks with decent scores, they're probably relevant
        return any(chunk.relevance_score > 1.0 for chunk in chunks)
    
    def _generate_intelligent_fallback(self, question: str) -> str:
        """Generate an intelligent fallback response for queries without specific information"""
        question_lower = question.lower()
        
        # Check if it's asking about specific equipment we don't know
        equipment_keywords = ['machine', 'equipment', 'device', 'system', 'unit']
        if any(keyword in question_lower for keyword in equipment_keywords):
            return f"""I don't have specific information about that equipment in my current manufacturing documentation.

For equipment-specific questions, I recommend:
1. **Consult the equipment manual** - Usually found near the machine or in the maintenance office
2. **Contact the equipment manufacturer** - They provide the most accurate technical support
3. **Reach out to our maintenance team** - Extension 2345 for immediate assistance

I can help with general manufacturing topics like safety procedures, common CNC and conveyor issues, and standard maintenance schedules. Is there anything specific about those areas I can assist with?"""

        # For completely unrelated queries, be helpful but redirect
        manufacturing_keywords = ['safety', 'maintenance', 'repair', 'troubleshoot', 'part', 'procedure', 'protocol']
        if not any(keyword in question_lower for keyword in manufacturing_keywords):
            return f"""I'm specialized in manufacturing assistance, so I might not be the best help for "{question}".

However, I'm here to help with:
🚨 **Safety procedures** and emergency protocols
🔧 **Equipment troubleshooting** and error codes
📋 **Maintenance schedules** and procedures
📦 **Parts information** and specifications

Is there anything manufacturing-related I can help you with today?"""

        # Default intelligent response for manufacturing-related but unknown queries
        return f"""I don't have specific information about "{question}" in my current manufacturing documentation.

I can help with:
- **Safety protocols** (lockout/tagout, emergency procedures)
- **Common error codes** (E001, E002) and troubleshooting
- **Maintenance schedules** for CNC machines and conveyor systems
- **Parts information** for standard equipment

Could you provide more details about what specific aspect you need help with? This will help me give you better assistance or direct you to the right resources."""

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