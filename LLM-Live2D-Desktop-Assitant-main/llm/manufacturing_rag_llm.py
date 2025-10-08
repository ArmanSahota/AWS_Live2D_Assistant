"""
Manufacturing RAG LLM Integration
=================================

This integrates the demo RAG functionality directly into your existing VTuber system.
It works as a drop-in replacement LLM provider that adds manufacturing knowledge.
"""

import sys
import os
import re
from typing import Iterator

# Add the parent directory to the path so we can import the demo RAG client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .llm_interface import LLMInterface

# Import from the parent directory where simple_s3_rag.py is located
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
try:
    from simple_s3_rag import SimpleS3RAG
except ImportError:
    # Fallback to demo RAG if S3 RAG not available
    from demo_rag_client import DemoManufacturingRAG as SimpleS3RAG
from demo_rag_client import ManufacturingContext

class LLM(LLMInterface):
    """
    Manufacturing RAG LLM that integrates with your existing VTuber system
    """
    
    def __init__(
        self,
        system: str = None,
        base_url: str = None,
        model: str = "manufacturing-rag-demo",
        verbose: bool = False,
        **kwargs
    ):
        self.system = system or self._get_manufacturing_system_prompt()
        self.base_url = base_url or 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev'
        self.model = model
        self.verbose = verbose
        
        # Initialize the Simple S3 RAG client
        self.rag_client = SimpleS3RAG()
        
        # Store conversation history for context
        self.conversation_history = []
        
        if self.verbose:
            print(f"🏭 Manufacturing S3 RAG LLM initialized")
            print(f"   Base URL: {self.base_url}")
            print(f"   Model: {self.model}")
            print(f"   S3 Bucket: live2d-aws-backend-documentsbucket-gvqh2hzqj761")
            print(f"   Document Source: Direct S3 retrieval (no OpenSearch required)")
    
    def _get_manufacturing_system_prompt(self) -> str:
        """Get the manufacturing-specific system prompt"""
        return """You are a specialized manufacturing assistant VTuber with access to technical documentation, 
        machine manuals, safety protocols, and troubleshooting guides. Your responses must:

        🚨 PRIORITIZE SAFETY: Always highlight safety warnings and precautions first
        📋 BE PRECISE: Provide exact part numbers, specifications, and procedures  
        📖 CITE SOURCES: Reference specific manuals or documents when available
        🗣️ USE CLEAR LANGUAGE: Explain technical terms, avoid unnecessary jargon
        📝 PROVIDE STEP-BY-STEP GUIDANCE: Break complex procedures into numbered steps
        ⚠️ HIGHLIGHT CRITICAL INFORMATION: Emphasize important warnings or specifications
        🔍 BE THOROUGH: Include relevant context like part numbers and compatibility

        You have access to manufacturing knowledge including:
        - Safety protocols (lockout/tagout, emergency procedures, PPE requirements)
        - Troubleshooting guides (error codes, common equipment issues)
        - Maintenance schedules (CNC machines, conveyor systems, etc.)
        - Parts catalogs (part numbers, specifications, replacement intervals)

        Format responses for voice output - use natural speech patterns and clear transitions.
        When you don't have specific information, clearly state this and recommend consulting 
        appropriate manuals or qualified technicians.
        """
    
    def _extract_manufacturing_context(self, prompt: str) -> ManufacturingContext:
        """Extract manufacturing context from the user's prompt"""
        context = ManufacturingContext()
        
        # Extract machine IDs
        machine_patterns = [
            r'machine\s+([A-Z0-9\-]+)',
            r'equipment\s+([A-Z0-9\-]+)', 
            r'unit\s+([A-Z0-9\-]+)',
            r'cnc\s*([0-9]+)?',
            r'conveyor\s*([0-9]+)?'
        ]
        
        for pattern in machine_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                context.machine_id = match.group(1) if match.group(1) else match.group(0)
                break
        
        # Extract error codes
        error_match = re.search(r'error\s+code\s+([A-Z0-9]+)|code\s+([A-Z0-9]+)', prompt, re.IGNORECASE)
        if error_match:
            context.error_code = error_match.group(1) or error_match.group(2)
        
        # Determine department
        departments = ['production', 'maintenance', 'quality', 'safety', 'engineering']
        for dept in departments:
            if dept in prompt.lower():
                context.department = dept
                break
        
        # Determine safety level
        safety_keywords = {
            'critical': ['emergency', 'danger', 'critical', 'stop'],
            'high': ['safety', 'warning', 'caution', 'hazard'],
            'medium': ['maintenance', 'service', 'check'],
            'low': ['information', 'general', 'question']
        }
        
        prompt_lower = prompt.lower()
        for level, keywords in safety_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                context.safety_level = level
                break
        
        return context
    
    def _is_manufacturing_query(self, prompt: str) -> bool:
        """Check if this is a manufacturing-related query"""
        manufacturing_keywords = [
            'machine', 'equipment', 'conveyor', 'cnc', 'robot', 'production',
            'maintenance', 'safety', 'lockout', 'tagout', 'emergency', 'error',
            'troubleshoot', 'part', 'component', 'repair', 'service', 'manual',
            'procedure', 'protocol', 'ppe', 'hazard', 'warning', 'spindle',
            'overload', 'fault', 'malfunction', 'broken', 'noise', 'code',
            'motor', 'bearing', 'hydraulic', 'pneumatic', 'electrical'
        ]
        
        prompt_lower = prompt.lower()
        
        # Check for error codes (E001, E002, etc.)
        if re.search(r'e\d+|error\s+code|code\s+\d+', prompt_lower):
            return True
            
        # Check for manufacturing keywords
        if any(keyword in prompt_lower for keyword in manufacturing_keywords):
            return True
            
        # Check for common manufacturing phrases
        manufacturing_phrases = [
            'what is this error', 'how to fix', 'troubleshooting', 'repair',
            'maintenance schedule', 'safety procedure', 'part number'
        ]
        
        if any(phrase in prompt_lower for phrase in manufacturing_phrases):
            return True
            
        return False
    
    def _combine_rag_with_conversation(self, prompt: str, rag_response: str) -> str:
        """Combine RAG knowledge with conversational context"""
        # Check if RAG found specific, relevant manufacturing info
        if rag_response and len(rag_response) > 100 and not "I can help you with manufacturing questions" in rag_response:
            # Add conversational elements to make it more natural
            conversational_response = f"Based on our manufacturing documentation, here's what I can tell you:\n\n{rag_response}"
            
            # Add context from conversation history if relevant
            if self.conversation_history:
                last_exchange = self.conversation_history[-1] if self.conversation_history else None
                if last_exchange and 'user' in last_exchange:
                    # Add continuity if this seems like a follow-up question
                    follow_up_indicators = ['also', 'what about', 'and', 'additionally', 'furthermore']
                    if any(indicator in prompt.lower() for indicator in follow_up_indicators):
                        conversational_response = f"Following up on our previous discussion, {conversational_response.lower()}"
            
            return conversational_response
        
        # For unknown queries, provide a more intelligent, contextual response
        return self._generate_intelligent_fallback_response(prompt)
    
    def _generate_intelligent_fallback_response(self, prompt: str) -> str:
        """Generate an intelligent fallback response for unknown queries"""
        prompt_lower = prompt.lower()
        
        # Check if it's asking about a specific error code we don't know
        error_code_match = re.search(r'error\s+code\s+([A-Z0-9]+)|code\s+([A-Z0-9]+)', prompt, re.IGNORECASE)
        if error_code_match:
            error_code = error_code_match.group(1) or error_code_match.group(2)
            return f"""I don't have specific information about error code {error_code} in my current knowledge base.

For unknown error codes, I recommend:
1. **Check your equipment manual** - Look for the specific error code section
2. **Contact your equipment manufacturer** - They'll have the most up-to-date error code definitions
3. **Document the symptoms** - Note what was happening when the error occurred
4. **Contact maintenance** - Extension 2345 for immediate assistance

I do have information about common error codes E001 (Spindle Overload) and E002 (Axis Drive Fault) if those are helpful."""

        # Check if it's asking about specific equipment we don't know
        equipment_keywords = ['machine', 'equipment', 'device', 'system', 'unit']
        if any(keyword in prompt_lower for keyword in equipment_keywords):
            return f"""I don't have specific information about that equipment in my current knowledge base.

For equipment-specific questions, I recommend:
1. **Consult the equipment manual** - Usually found near the machine or in the maintenance office
2. **Contact the equipment manufacturer** - They provide the most accurate technical support
3. **Reach out to our maintenance team** - Extension 2345 for immediate assistance

I can help with general manufacturing topics like safety procedures, common CNC and conveyor issues, and standard maintenance schedules. Is there anything specific about those areas I can assist with?"""

        # For completely unrelated queries, be helpful but redirect
        manufacturing_keywords = ['safety', 'maintenance', 'repair', 'troubleshoot', 'part', 'procedure', 'protocol']
        if not any(keyword in prompt_lower for keyword in manufacturing_keywords):
            return f"""I'm specialized in manufacturing assistance, so I might not be the best help for "{prompt}".

However, I'm here to help with:
🚨 **Safety procedures** and emergency protocols
🔧 **Equipment troubleshooting** and error codes
📋 **Maintenance schedules** and procedures
📦 **Parts information** and specifications

Is there anything manufacturing-related I can help you with today?"""

        # Default intelligent response for manufacturing-related but unknown queries
        return f"""I understand you're asking about "{prompt}" but I don't have specific information on that topic in my current knowledge base.

I can help with:
- **Safety protocols** (lockout/tagout, emergency procedures)
- **Common error codes** (E001, E002) and troubleshooting
- **Maintenance schedules** for CNC machines and conveyor systems
- **Parts information** for standard equipment

Could you provide more details about what specific aspect you need help with? This will help me give you better assistance or direct you to the right resources."""
    
    def _handle_general_query(self, prompt: str) -> str:
        """Handle general queries in a helpful way while guiding toward manufacturing topics"""
        prompt_lower = prompt.lower()
        
        # Check if it's a greeting or casual question
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'how are you', "what's up"]
        if any(greeting in prompt_lower for greeting in greetings):
            return """Hello! I'm your manufacturing assistant. I'm here to help with equipment troubleshooting, safety procedures, maintenance schedules, and more. What can I assist you with today?"""
        
        # Check if it's asking for general help or capabilities
        help_keywords = ['help', 'what can you do', 'capabilities', 'assist', 'support']
        if any(keyword in prompt_lower for keyword in help_keywords):
            return """I'm a specialized manufacturing assistant that can help you with:

🚨 **Safety & Emergency**: Lockout/tagout procedures, emergency protocols, PPE requirements
🔧 **Troubleshooting**: Error codes (E001, E002), equipment diagnostics, repair guidance
📋 **Maintenance**: Schedules for CNC machines, conveyor systems, preventive maintenance
📦 **Parts & Specifications**: Part numbers, replacement procedures, technical specifications

I can also try to help with general questions when possible. What would you like assistance with?"""
        
        # Check if it's asking about something that might be technical but not clearly manufacturing
        technical_keywords = ['error', 'problem', 'issue', 'broken', 'fix', 'repair', 'troubleshoot']
        if any(keyword in prompt_lower for keyword in technical_keywords):
            return f"""I can see you're dealing with "{prompt}". While I specialize in manufacturing equipment, I can try to help!

If this is related to:
- **Industrial equipment** - I have detailed troubleshooting guides
- **Error codes** - I know about common codes like E001, E002
- **Mechanical issues** - I can provide general repair guidance
- **Safety concerns** - I have comprehensive safety protocols

Could you provide more details about what type of equipment or system you're working with? This will help me give you the most relevant assistance."""
        
        # For other general questions, be helpful but guide toward manufacturing
        return f"""I'll do my best to help with "{prompt}"! While I specialize in manufacturing assistance, I can try to provide general guidance.

However, I'm most effective when helping with:
🏭 **Manufacturing Operations**: Equipment troubleshooting, maintenance schedules
🚨 **Safety Protocols**: Emergency procedures, PPE requirements
🔧 **Technical Support**: Error codes, repair procedures
📋 **Documentation**: Machine manuals, parts information

Is there a manufacturing or technical aspect to your question I can focus on?"""
    
    def chat_iter(self, prompt: str, image_base64=None) -> Iterator[str]:
        """
        Main chat method that integrates RAG with conversational AI
        """
        try:
            if self.verbose:
                print(f"🏭 Manufacturing RAG processing: {prompt[:100]}...")
            
            # Extract manufacturing context
            context = self._extract_manufacturing_context(prompt)
            
            # Check if this is a manufacturing query
            is_manufacturing = self._is_manufacturing_query(prompt)
            
            if is_manufacturing:
                # Get RAG response for manufacturing queries
                rag_response = self.rag_client.query(prompt)
                
                # Combine with conversational context
                final_response = self._combine_rag_with_conversation(prompt, rag_response)
                
                if self.verbose:
                    print(f"🔧 Manufacturing query detected - using RAG knowledge")
                    print(f"📋 Context: Machine={context.machine_id}, Error={context.error_code}, Safety={context.safety_level}")
            
            else:
                # For non-manufacturing queries, try to be helpful while guiding toward manufacturing
                final_response = self._handle_general_query(prompt)
                
                if self.verbose:
                    print(f"💬 General query - providing helpful response with manufacturing guidance")
            
            # Store in conversation history
            self.conversation_history.append({
                'user': prompt,
                'assistant': final_response,
                'context': context,
                'is_manufacturing': is_manufacturing
            })
            
            # Keep history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-8:]
            
            # Stream the response character by character for natural speech
            for char in final_response:
                yield char
                
        except Exception as e:
            error_response = f"I encountered an issue processing your request: {str(e)}. Please try rephrasing your question or ask about specific manufacturing topics like safety procedures, equipment troubleshooting, or maintenance schedules."
            
            if self.verbose:
                print(f"❌ Error in manufacturing RAG: {e}")
            
            for char in error_response:
                yield char
    
    def handle_interrupt(self, heard_response: str) -> None:
        """
        Handle interruption during response generation
        """
        if self.verbose:
            print(f"🛑 Manufacturing RAG interrupted at: {heard_response[:50]}...")
        
        # Update the last conversation entry to reflect what was actually heard
        if self.conversation_history:
            self.conversation_history[-1]['assistant'] = heard_response
            self.conversation_history[-1]['interrupted'] = True
        
        # Note: For a demo, we don't need complex interrupt handling
        # In a full implementation, this could trigger follow-up clarification