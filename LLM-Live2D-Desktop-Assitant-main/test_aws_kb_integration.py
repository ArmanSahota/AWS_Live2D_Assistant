#!/usr/bin/env python3
"""
AWS Knowledge Base Integration Testing Script
Comprehensive testing suite for AWS Knowledge Base RAG integration
"""

import os
import sys
import json
import asyncio
import aiohttp
import time
from typing import Dict, Any, List
import argparse
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from aws_knowledge_base_rag import AWSKnowledgeBaseRAG, HybridRAGSystem, create_rag_system
    AWS_KB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AWS Knowledge Base RAG not available: {e}")
    AWS_KB_AVAILABLE = False

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    print("Warning: boto3 not available")
    BOTO3_AVAILABLE = False


class AWSKBIntegrationTester:
    """Comprehensive testing suite for AWS Knowledge Base integration"""
    
    def __init__(self, config_file: str = ".env"):
        """
        Initialize the tester
        
        Args:
            config_file: Path to configuration file
        """
        self.config = self._load_config(config_file)
        self.knowledge_base_id = self.config.get('AWS_KNOWLEDGE_BASE_ID')
        self.region = self.config.get('AWS_REGION', 'us-west-2')
        self.bucket_name = self.config.get('DOCUMENTS_BUCKET_NAME')
        self.http_api_base = self.config.get('HTTP_API_BASE')
        
        print(f"Initialized tester with:")
        print(f"  Knowledge Base ID: {self.knowledge_base_id}")
        print(f"  Region: {self.region}")
        print(f"  Bucket: {self.bucket_name}")
        print(f"  API Base: {self.http_api_base}")
    
    def _load_config(self, config_file: str) -> Dict[str, str]:
        """Load configuration from file"""
        config = {}
        
        # Load from .env file
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        
        # Override with environment variables
        for key, value in os.environ.items():
            if key.startswith(('AWS_', 'RAG_', 'DOCUMENTS_')):
                config[key] = value
        
        return config
    
    async def test_aws_kb_direct(self) -> Dict[str, Any]:
        """Test AWS Knowledge Base directly"""
        print("\n" + "="*60)
        print("TEST 1: AWS Knowledge Base Direct Access")
        print("="*60)
        
        if not AWS_KB_AVAILABLE:
            return {"status": "skipped", "reason": "AWS KB RAG not available"}
        
        if not self.knowledge_base_id:
            return {"status": "skipped", "reason": "No Knowledge Base ID configured"}
        
        try:
            # Initialize AWS KB RAG
            aws_rag = AWSKnowledgeBaseRAG(
                knowledge_base_id=self.knowledge_base_id,
                region=self.region
            )
            
            # Health check
            health = aws_rag.health_check()
            print(f"Health check: {json.dumps(health, indent=2)}")
            
            if not aws_rag.is_available():
                return {"status": "failed", "reason": "AWS KB not available", "health": health}
            
            # Test queries
            test_queries = [
                "What should I do for heater error 103?",
                "What are the safety procedures for equipment maintenance?",
                "How do I classify defects in quality control?",
                "What is the daily maintenance checklist?"
            ]
            
            results = []
            for query in test_queries:
                print(f"\nTesting query: {query}")
                start_time = time.time()
                
                response = aws_rag.get_rag_response(query)
                
                end_time = time.time()
                query_time = end_time - start_time
                
                print(f"  Sources found: {response.sources_used}")
                print(f"  Query time: {query_time:.3f}s")
                print(f"  Enhanced prompt length: {len(response.enhanced_prompt)} chars")
                
                if response.documents:
                    print("  Top documents:")
                    for i, doc in enumerate(response.documents[:2], 1):
                        print(f"    {i}. {doc.source} (score: {doc.score:.3f})")
                        print(f"       {doc.content[:100]}...")
                
                results.append({
                    "query": query,
                    "sources_used": response.sources_used,
                    "query_time": query_time,
                    "enhanced_prompt_length": len(response.enhanced_prompt)
                })
            
            return {
                "status": "success",
                "health": health,
                "query_results": results,
                "total_queries": len(test_queries)
            }
            
        except Exception as e:
            print(f"Error in AWS KB direct test: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_hybrid_rag_system(self) -> Dict[str, Any]:
        """Test hybrid RAG system"""
        print("\n" + "="*60)
        print("TEST 2: Hybrid RAG System")
        print("="*60)
        
        if not AWS_KB_AVAILABLE:
            return {"status": "skipped", "reason": "AWS KB RAG not available"}
        
        try:
            # Create hybrid RAG system
            rag_system = create_rag_system(self.config)
            
            # Health check
            health = rag_system.health_check()
            print(f"Hybrid system health: {json.dumps(health, indent=2)}")
            
            # Test queries
            test_queries = [
                "manufacturing error troubleshooting",
                "safety protocols for maintenance",
                "quality control procedures"
            ]
            
            results = []
            for query in test_queries:
                print(f"\nTesting hybrid query: {query}")
                start_time = time.time()
                
                response = rag_system.get_context(query)
                
                end_time = time.time()
                query_time = end_time - start_time
                
                print(f"  Sources found: {response.sources_used}")
                print(f"  Knowledge base: {response.knowledge_base_id}")
                print(f"  Query time: {query_time:.3f}s")
                
                results.append({
                    "query": query,
                    "sources_used": response.sources_used,
                    "knowledge_base_id": response.knowledge_base_id,
                    "query_time": query_time
                })
            
            return {
                "status": "success",
                "health": health,
                "query_results": results
            }
            
        except Exception as e:
            print(f"Error in hybrid RAG test: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_enhanced_server_integration(self) -> Dict[str, Any]:
        """Test integration with enhanced server"""
        print("\n" + "="*60)
        print("TEST 3: Enhanced Server Integration")
        print("="*60)
        
        # Test if enhanced server is running
        server_url = "http://localhost:8000"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{server_url}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"Server health: {json.dumps(health_data, indent=2)}")
                    else:
                        return {"status": "failed", "reason": f"Server health check failed: {response.status}"}
                
                # Test RAG health endpoint
                try:
                    async with session.get(f"{server_url}/rag/health") as response:
                        if response.status == 200:
                            rag_health = await response.json()
                            print(f"RAG health: {json.dumps(rag_health, indent=2)}")
                        else:
                            print(f"RAG health endpoint returned: {response.status}")
                except Exception as e:
                    print(f"RAG health endpoint error: {e}")
                
                # Test Claude endpoint with RAG
                test_requests = [
                    {
                        "text": "What should I do if I encounter heater error 103?",
                        "enable_rag": True,
                        "rag_mode": "hybrid"
                    },
                    {
                        "text": "What are the safety procedures for equipment maintenance?",
                        "enable_rag": True,
                        "rag_mode": "aws"
                    },
                    {
                        "text": "How do I perform quality control inspections?",
                        "enable_rag": False
                    }
                ]
                
                results = []
                for i, request_data in enumerate(test_requests, 1):
                    print(f"\nTesting Claude request {i}: {request_data['text'][:50]}...")
                    
                    try:
                        async with session.post(
                            f"{server_url}/claude",
                            json=request_data,
                            headers={"Content-Type": "application/json"}
                        ) as response:
                            if response.status == 200:
                                result = await response.json()
                                print(f"  Status: Success")
                                print(f"  RAG enabled: {result.get('rag_metadata', {}).get('rag_enabled', False)}")
                                print(f"  Sources used: {result.get('rag_metadata', {}).get('sources_used', 0)}")
                                print(f"  Response length: {len(result.get('reply', ''))}")
                                
                                results.append({
                                    "request": request_data,
                                    "status": "success",
                                    "rag_metadata": result.get('rag_metadata', {}),
                                    "response_length": len(result.get('reply', ''))
                                })
                            else:
                                error_text = await response.text()
                                print(f"  Status: Failed ({response.status})")
                                print(f"  Error: {error_text}")
                                
                                results.append({
                                    "request": request_data,
                                    "status": "failed",
                                    "error": error_text
                                })
                    except Exception as e:
                        print(f"  Error: {e}")
                        results.append({
                            "request": request_data,
                            "status": "error",
                            "error": str(e)
                        })
                
                return {
                    "status": "success",
                    "server_health": health_data,
                    "claude_requests": results
                }
                
        except aiohttp.ClientConnectorError:
            return {"status": "failed", "reason": "Cannot connect to server. Is it running?"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def test_aws_lambda_integration(self) -> Dict[str, Any]:
        """Test AWS Lambda integration"""
        print("\n" + "="*60)
        print("TEST 4: AWS Lambda Integration")
        print("="*60)
        
        if not self.http_api_base:
            return {"status": "skipped", "reason": "No HTTP API base URL configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{self.http_api_base}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"Lambda health: {json.dumps(health_data, indent=2)}")
                    else:
                        return {"status": "failed", "reason": f"Lambda health check failed: {response.status}"}
                
                # Test Claude endpoint
                test_request = {
                    "text": "What should I do for heater error 103?",
                    "enable_rag": True,
                    "system": "You are a manufacturing assistant with access to technical documentation."
                }
                
                print(f"\nTesting Lambda Claude endpoint...")
                async with session.post(
                    f"{self.http_api_base}/claude",
                    json=test_request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"  Status: Success")
                        print(f"  RAG enabled: {result.get('rag_enabled', False)}")
                        print(f"  Sources used: {result.get('sources_used', 0)}")
                        print(f"  Knowledge Base ID: {result.get('knowledge_base_id', 'N/A')}")
                        
                        return {
                            "status": "success",
                            "health": health_data,
                            "claude_result": result
                        }
                    else:
                        error_text = await response.text()
                        return {"status": "failed", "error": error_text}
                        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def test_document_retrieval_accuracy(self) -> Dict[str, Any]:
        """Test document retrieval accuracy"""
        print("\n" + "="*60)
        print("TEST 5: Document Retrieval Accuracy")
        print("="*60)
        
        if not AWS_KB_AVAILABLE or not self.knowledge_base_id:
            return {"status": "skipped", "reason": "AWS KB not available"}
        
        try:
            aws_rag = AWSKnowledgeBaseRAG(
                knowledge_base_id=self.knowledge_base_id,
                region=self.region
            )
            
            # Test specific queries that should match known documents
            accuracy_tests = [
                {
                    "query": "heater error 103",
                    "expected_keywords": ["heater", "error", "103", "temperature", "safety"],
                    "expected_sources": ["heater_error_103_documentation.md"]
                },
                {
                    "query": "quality control defect classification",
                    "expected_keywords": ["quality", "defect", "class", "critical", "major"],
                    "expected_sources": ["quality_control_procedures.md"]
                },
                {
                    "query": "equipment maintenance schedule",
                    "expected_keywords": ["maintenance", "daily", "weekly", "monthly", "equipment"],
                    "expected_sources": ["equipment_maintenance_schedule.md"]
                }
            ]
            
            results = []
            for test in accuracy_tests:
                print(f"\nTesting accuracy for: {test['query']}")
                
                documents = aws_rag.retrieve_documents(test['query'], max_results=5)
                
                # Check if expected keywords are found
                keyword_matches = 0
                for doc in documents:
                    content_lower = doc.content.lower()
                    for keyword in test['expected_keywords']:
                        if keyword.lower() in content_lower:
                            keyword_matches += 1
                            break
                
                # Check if expected sources are found
                source_matches = 0
                found_sources = [doc.source for doc in documents]
                for expected_source in test['expected_sources']:
                    if any(expected_source in source for source in found_sources):
                        source_matches += 1
                
                accuracy_score = (keyword_matches + source_matches) / (len(test['expected_keywords']) + len(test['expected_sources']))
                
                print(f"  Documents found: {len(documents)}")
                print(f"  Keyword matches: {keyword_matches}/{len(test['expected_keywords'])}")
                print(f"  Source matches: {source_matches}/{len(test['expected_sources'])}")
                print(f"  Accuracy score: {accuracy_score:.2f}")
                
                results.append({
                    "query": test['query'],
                    "documents_found": len(documents),
                    "keyword_matches": keyword_matches,
                    "source_matches": source_matches,
                    "accuracy_score": accuracy_score,
                    "found_sources": found_sources
                })
            
            overall_accuracy = sum(r['accuracy_score'] for r in results) / len(results)
            
            return {
                "status": "success",
                "overall_accuracy": overall_accuracy,
                "test_results": results
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        print("Starting AWS Knowledge Base Integration Tests...")
        print("="*80)
        
        test_results = {}
        
        # Run all tests
        test_results['aws_kb_direct'] = await self.test_aws_kb_direct()
        test_results['hybrid_rag_system'] = await self.test_hybrid_rag_system()
        test_results['enhanced_server'] = await self.test_enhanced_server_integration()
        test_results['aws_lambda'] = await self.test_aws_lambda_integration()
        test_results['retrieval_accuracy'] = await self.test_document_retrieval_accuracy()
        
        # Generate summary
        total_tests = len(test_results)
        successful_tests = sum(1 for result in test_results.values() if result.get('status') == 'success')
        failed_tests = sum(1 for result in test_results.values() if result.get('status') == 'failed')
        error_tests = sum(1 for result in test_results.values() if result.get('status') == 'error')
        skipped_tests = sum(1 for result in test_results.values() if result.get('status') == 'skipped')
        
        summary = {
            "total_tests": total_tests,
            "successful": successful_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "skipped": skipped_tests,
            "success_rate": successful_tests / total_tests if total_tests > 0 else 0
        }
        
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        
        # Detailed results
        for test_name, result in test_results.items():
            status = result.get('status', 'unknown')
            print(f"\n{test_name.upper()}: {status.upper()}")
            if status == 'failed':
                print(f"  Reason: {result.get('reason', 'Unknown')}")
            elif status == 'error':
                print(f"  Error: {result.get('error', 'Unknown')}")
        
        return {
            "summary": summary,
            "test_results": test_results,
            "timestamp": time.time()
        }
    
    def save_report(self, results: Dict[str, Any], filename: str = "aws_kb_test_report.json") -> None:
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nTest report saved to: {filename}")


async def main():
    parser = argparse.ArgumentParser(description="Test AWS Knowledge Base Integration")
    parser.add_argument("--config", default=".env", help="Configuration file")
    parser.add_argument("--test", choices=['all', 'aws-kb', 'hybrid', 'server', 'lambda', 'accuracy'], 
                       default='all', help="Specific test to run")
    parser.add_argument("--save-report", action="store_true", help="Save test report to file")
    
    args = parser.parse_args()
    
    tester = AWSKBIntegrationTester(args.config)
    
    if args.test == 'all':
        results = await tester.run_all_tests()
    elif args.test == 'aws-kb':
        results = {"aws_kb_direct": await tester.test_aws_kb_direct()}
    elif args.test == 'hybrid':
        results = {"hybrid_rag_system": await tester.test_hybrid_rag_system()}
    elif args.test == 'server':
        results = {"enhanced_server": await tester.test_enhanced_server_integration()}
    elif args.test == 'lambda':
        results = {"aws_lambda": await tester.test_aws_lambda_integration()}
    elif args.test == 'accuracy':
        results = {"retrieval_accuracy": await tester.test_document_retrieval_accuracy()}
    
    if args.save_report:
        tester.save_report(results)
    
    # Exit with appropriate code
    if args.test == 'all':
        success_rate = results.get('summary', {}).get('success_rate', 0)
        sys.exit(0 if success_rate > 0.5 else 1)
    else:
        test_result = list(results.values())[0]
        sys.exit(0 if test_result.get('status') == 'success' else 1)


if __name__ == "__main__":
    asyncio.run(main())