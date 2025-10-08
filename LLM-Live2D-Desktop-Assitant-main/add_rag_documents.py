#!/usr/bin/env python3
"""
RAG Document Ingestion Script
Adds manufacturing error documentation to the RAG system for enhanced AI analysis
"""

import os
import sys
import json
import boto3
from pathlib import Path
from typing import List, Dict, Any
import hashlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGDocumentIngester:
    def __init__(self, config_file: str = "manufacturing-assistant-config.yaml"):
        """Initialize the RAG document ingester"""
        self.config_file = config_file
        self.documents_dir = Path("rag_documents")
        self.s3_client = None
        self.opensearch_client = None
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            import yaml
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def setup_aws_clients(self):
        """Setup AWS clients for S3 and OpenSearch"""
        try:
            # Setup S3 client
            self.s3_client = boto3.client('s3')
            
            # Setup OpenSearch client (if configured)
            if 'opensearch' in self.config:
                from opensearchpy import OpenSearch, RequestsHttpConnection
                from requests_aws4auth import AWS4Auth
                
                credentials = boto3.Session().get_credentials()
                awsauth = AWS4Auth(
                    credentials.access_key,
                    credentials.secret_key,
                    'us-east-1',  # Adjust region as needed
                    'es',
                    session_token=credentials.token
                )
                
                self.opensearch_client = OpenSearch(
                    hosts=[{'host': self.config['opensearch']['endpoint'], 'port': 443}],
                    http_auth=awsauth,
                    use_ssl=True,
                    verify_certs=True,
                    connection_class=RequestsHttpConnection
                )
                
            logger.info("AWS clients setup successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup AWS clients: {e}")
            
    def process_documents(self) -> List[Dict[str, Any]]:
        """Process all documents in the rag_documents directory"""
        documents = []
        
        if not self.documents_dir.exists():
            logger.warning(f"Documents directory {self.documents_dir} does not exist")
            return documents
            
        for doc_file in self.documents_dir.glob("*.md"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create document metadata
                doc_id = hashlib.md5(doc_file.name.encode()).hexdigest()
                document = {
                    'id': doc_id,
                    'filename': doc_file.name,
                    'title': self.extract_title(content),
                    'content': content,
                    'type': 'manufacturing_documentation',
                    'category': self.categorize_document(doc_file.name),
                    'size': len(content),
                    'created_at': doc_file.stat().st_mtime
                }
                
                documents.append(document)
                logger.info(f"Processed document: {doc_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to process {doc_file}: {e}")
                
        return documents
    
    def extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled Document"
    
    def categorize_document(self, filename: str) -> str:
        """Categorize document based on filename"""
        filename_lower = filename.lower()
        
        if 'error' in filename_lower:
            return 'error_documentation'
        elif 'heater' in filename_lower:
            return 'heating_systems'
        elif 'manufacturing' in filename_lower:
            return 'manufacturing_processes'
        elif 'safety' in filename_lower:
            return 'safety_procedures'
        else:
            return 'general_documentation'
    
    def upload_to_s3(self, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to S3 bucket"""
        if not self.s3_client or 'aws' not in self.config:
            logger.warning("S3 client not configured, skipping S3 upload")
            return False
            
        try:
            bucket_name = self.config['aws'].get('s3_bucket', 'manufacturing-rag-documents')
            
            for doc in documents:
                key = f"documents/{doc['filename']}"
                
                # Upload document content
                self.s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=doc['content'],
                    ContentType='text/markdown',
                    Metadata={
                        'title': doc['title'],
                        'category': doc['category'],
                        'type': doc['type']
                    }
                )
                
                logger.info(f"Uploaded {doc['filename']} to S3")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False
    
    def index_to_opensearch(self, documents: List[Dict[str, Any]]) -> bool:
        """Index documents to OpenSearch for vector search"""
        if not self.opensearch_client:
            logger.warning("OpenSearch client not configured, skipping indexing")
            return False
            
        try:
            index_name = 'manufacturing-documents'
            
            # Create index if it doesn't exist
            if not self.opensearch_client.indices.exists(index=index_name):
                index_body = {
                    'mappings': {
                        'properties': {
                            'title': {'type': 'text'},
                            'content': {'type': 'text'},
                            'category': {'type': 'keyword'},
                            'type': {'type': 'keyword'},
                            'filename': {'type': 'keyword'},
                            'created_at': {'type': 'date'},
                            'embedding': {
                                'type': 'dense_vector',
                                'dims': 1536  # OpenAI embedding dimension
                            }
                        }
                    }
                }
                
                self.opensearch_client.indices.create(
                    index=index_name,
                    body=index_body
                )
                logger.info(f"Created OpenSearch index: {index_name}")
            
            # Index documents
            for doc in documents:
                self.opensearch_client.index(
                    index=index_name,
                    id=doc['id'],
                    body={
                        'title': doc['title'],
                        'content': doc['content'],
                        'category': doc['category'],
                        'type': doc['type'],
                        'filename': doc['filename'],
                        'created_at': doc['created_at']
                    }
                )
                
                logger.info(f"Indexed {doc['filename']} to OpenSearch")
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to index to OpenSearch: {e}")
            return False
    
    def save_local_index(self, documents: List[Dict[str, Any]]) -> bool:
        """Save documents to local JSON index for fallback"""
        try:
            index_file = Path("rag_documents_index.json")
            
            index_data = {
                'documents': documents,
                'total_count': len(documents),
                'last_updated': import_time.time(),
                'categories': list(set(doc['category'] for doc in documents))
            }
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved local index with {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save local index: {e}")
            return False
    
    def run(self):
        """Main execution method"""
        logger.info("Starting RAG document ingestion process")
        
        # Process documents
        documents = self.process_documents()
        if not documents:
            logger.warning("No documents found to process")
            return
            
        logger.info(f"Found {len(documents)} documents to process")
        
        # Setup AWS clients
        self.setup_aws_clients()
        
        # Upload to various destinations
        success_count = 0
        
        # Save local index (always do this)
        if self.save_local_index(documents):
            success_count += 1
            
        # Upload to S3 (if configured)
        if self.upload_to_s3(documents):
            success_count += 1
            
        # Index to OpenSearch (if configured)
        if self.index_to_opensearch(documents):
            success_count += 1
            
        logger.info(f"Document ingestion completed. {success_count} operations successful.")
        
        # Print summary
        print("\n" + "="*50)
        print("RAG DOCUMENT INGESTION SUMMARY")
        print("="*50)
        print(f"Documents processed: {len(documents)}")
        print(f"Categories found: {len(set(doc['category'] for doc in documents))}")
        print("\nDocument categories:")
        for category in set(doc['category'] for doc in documents):
            count = sum(1 for doc in documents if doc['category'] == category)
            print(f"  - {category}: {count} documents")
        print("\nDocuments are now ready for RAG-enhanced AI analysis!")

def main():
    """Main entry point"""
    import time as import_time
    
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "manufacturing-assistant-config.yaml"
        
    ingester = RAGDocumentIngester(config_file)
    ingester.run()

if __name__ == "__main__":
    main()