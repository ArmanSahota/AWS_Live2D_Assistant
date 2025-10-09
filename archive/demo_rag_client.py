#!/usr/bin/env python3
"""
Demo RAG Client for Manufacturing VTuber Assistant
==================================================

This is a simplified RAG implementation for demo/proof-of-concept purposes.
It uses pre-loaded manufacturing knowledge instead of complex vector databases.

Usage:
    from demo_rag_client import DemoManufacturingRAG
    
    client = DemoManufacturingRAG()
    response = client.query("What is lockout tagout procedure?")
    print(response)
"""

import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ManufacturingContext:
    """Simple context for manufacturing queries"""
    machine_id: Optional[str] = None
    error_code: Optional[str] = None
    department: Optional[str] = None
    safety_level: Optional[str] = None

class DemoManufacturingRAG:
    """
    Demo RAG client with pre-loaded manufacturing knowledge
    Perfect for proof-of-concept without complex AWS setup
    """
    
    def __init__(self, base_url: str = 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev'):
        self.base_url = base_url
        
        # Pre-loaded manufacturing knowledge base
        self.knowledge_base = {
            'safety_protocols': {
                'lockout_tagout': """
🚨 LOCKOUT/TAGOUT PROCEDURE:

1. **NOTIFY** all affected personnel before starting
2. **SHUTDOWN** equipment using normal stopping procedure  
3. **ISOLATE** all energy sources:
   - Electrical: Turn off breakers, remove fuses
   - Pneumatic: Close air valves, bleed lines
   - Hydraulic: Close valves, relieve pressure
4. **APPLY** lockout/tagout devices to energy isolation points
5. **VERIFY** isolation by attempting to start equipment
6. **PERFORM** maintenance work safely
7. **REMOVE** lockout/tagout devices ONLY by authorized person who applied them

⚠️ CRITICAL: Never remove another person's lock or tag!
""",
                'emergency_stop': """
🚨 EMERGENCY SHUTDOWN PROCEDURE:

1. **PRESS** red emergency stop button (located every 50 feet)
2. **EVACUATE** immediate area if safe to do so
3. **CALL** emergency response: Extension 2911 or 911
4. **SECURE** area - prevent others from entering
5. **REPORT** to supervisor immediately
6. **DO NOT** restart equipment until cleared by safety personnel

Emergency stop buttons are located:
- Main production floor: Every 50 feet
- Each workstation
- Equipment control panels
""",
                'ppe_requirements': """
⚠️ PERSONAL PROTECTIVE EQUIPMENT (PPE):

**Production Floor (General)**:
- Safety glasses (ANSI Z87.1)
- Steel-toed boots
- Hard hat in overhead work zones

**Welding Area**:
- Welding helmet with proper shade lens
- Leather welding gloves
- Fire-resistant clothing
- Respiratory protection if required

**High-Noise Areas (>85dB)**:
- Hearing protection (earplugs or earmuffs)
- Areas marked with yellow signs

**Chemical Handling**:
- Chemical-resistant gloves
- Safety goggles
- Apron or protective clothing
"""
            },
            
            'troubleshooting': {
                'error_codes': {
                    'E001': """
🔧 ERROR CODE E001 - Spindle Overload

**Possible Causes**:
- Dull or damaged cutting tools
- Excessive feed rate
- Insufficient coolant flow
- Material too hard for current setup

**Troubleshooting Steps**:
1. **STOP** machine immediately
2. **CHECK** cutting tool condition - replace if dull
3. **REDUCE** feed rate by 25%
4. **VERIFY** coolant flow and pressure
5. **INSPECT** workpiece material specifications
6. **RESTART** with reduced parameters

**Part Numbers**:
- Replacement cutting tools: CT-001, CT-002
- Coolant pump: CP-500
""",
                    'E002': """
🔧 ERROR CODE E002 - Axis Drive Fault

**Possible Causes**:
- Motor connection loose
- Encoder cable damaged
- Drive parameters incorrect
- Mechanical binding

**Troubleshooting Steps**:
1. **POWER DOWN** system safely
2. **CHECK** all motor connections
3. **INSPECT** encoder cables for damage
4. **VERIFY** mechanical movement is free
5. **RESET** drive parameters if needed
6. **CONTACT** maintenance if problem persists

**Part Numbers**:
- Encoder cable: EC-100
- Motor connector: MC-50
"""
                },
                
                'common_issues': {
                    'conveyor_noise': """
🔧 CONVEYOR BELT UNUSUAL NOISE

**Diagnostic Steps**:
1. **IDENTIFY** noise type:
   - Squealing: Belt tension or bearing issue
   - Grinding: Bearing failure
   - Clicking: Loose fasteners

2. **INSPECT** visually:
   - Belt alignment and tension
   - Roller condition
   - Motor mounting

3. **IMMEDIATE ACTIONS**:
   - Reduce speed if safe
   - Apply temporary lubrication to bearings
   - Schedule maintenance

**Part Numbers**:
- Conveyor belt: CV-BELT-001
- Roller bearings: RB-25
- Belt tensioner: BT-10
""",
                    'robot_not_responding': """
🔧 ROBOT ARM NOT RESPONDING

**Safety First**: Ensure emergency stop is accessible

**Troubleshooting Steps**:
1. **CHECK** power indicators on control panel
2. **VERIFY** emergency stops are not engaged
3. **INSPECT** teach pendant connection
4. **REVIEW** error messages on display
5. **RESTART** controller if no errors shown
6. **CONTACT** robotics technician if unresolved

**Emergency Contacts**:
- Robotics Tech: Extension 3456
- Maintenance: Extension 2345
"""
                }
            },
            
            'maintenance': {
                'schedules': {
                    'cnc_machine': """
📋 CNC MACHINE MAINTENANCE SCHEDULE

**Daily**:
- Check coolant levels
- Inspect cutting tools for wear
- Clean work area and remove chips
- Verify emergency stops function

**Weekly**:
- Lubricate guide ways
- Check hydraulic fluid levels  
- Inspect air filters
- Calibrate tool offsets

**Monthly**:
- Replace air filters
- Check belt tension
- Inspect electrical connections
- Update maintenance log

**Quarterly**:
- Full spindle inspection
- Replace coolant
- Calibrate machine accuracy
""",
                    'conveyor_system': """
📋 CONVEYOR SYSTEM MAINTENANCE

**Daily**:
- Visual inspection of belt condition
- Check for unusual noises
- Verify proper tracking

**Weekly**:
- Lubricate roller bearings
- Check belt tension
- Clean debris from rollers

**Monthly**:
- Inspect motor connections
- Check drive alignment
- Replace worn rollers if needed

**Part Replacement Schedule**:
- Belt: Every 6 months (CV-BELT-001)
- Rollers: Every 2 years (CV-ROLLER-001)
- Motor: Every 5 years (CV-MOTOR-001)
"""
                }
            },
            
            'parts_catalog': {
                'conveyor_parts': """
📦 CONVEYOR SYSTEM PARTS

**Belt Assembly**:
- Part #: CV-BELT-001
- Size: 50ft x 12in
- Material: Reinforced rubber
- Replacement interval: 6 months

**Drive Motor**:
- Part #: CV-MOTOR-001  
- Power: 5HP, 3-phase
- RPM: 1750
- Replacement interval: 5 years

**Roller Set**:
- Part #: CV-ROLLER-001
- Quantity: Set of 10
- Bearing type: Sealed
- Replacement interval: 2 years

**Belt Tensioner**:
- Part #: BT-10
- Adjustment range: 2-6 inches
- Material: Steel with rubber pad
""",
                'cnc_parts': """
📦 CNC MACHINE PARTS

**Spindle Motor**:
- Part #: CNC-SPIN-001
- Power: 15HP
- Max RPM: 8000
- Replacement interval: 10 years

**Tool Changer**:
- Part #: CNC-ATC-001
- Capacity: 20 tools
- Change time: 3 seconds
- Replacement interval: 7 years

**Coolant Pump**:
- Part #: CNC-COOL-001
- Flow rate: 50 GPM
- Pressure: 100 PSI
- Replacement interval: 3 years

**Cutting Tools**:
- Carbide inserts: CT-001, CT-002
- End mills: EM-10, EM-20
- Drill bits: DB-series
"""
            }
        }
        
        # Query patterns for matching
        self.query_patterns = {
            'safety': ['safety', 'lockout', 'tagout', 'emergency', 'stop', 'ppe', 'protection'],
            'troubleshooting': ['error', 'code', 'problem', 'fault', 'malfunction', 'broken', 'noise'],
            'maintenance': ['maintenance', 'schedule', 'service', 'lubricate', 'replace', 'inspect'],
            'parts': ['part', 'number', 'component', 'spare', 'replacement', 'catalog']
        }
    
    def extract_context(self, query: str) -> ManufacturingContext:
        """Extract manufacturing context from query"""
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
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                context.machine_id = match.group(1) if match.group(1) else match.group(0)
                break
        
        # Extract error codes
        error_match = re.search(r'error\s+code\s+([A-Z0-9]+)|code\s+([A-Z0-9]+)', query, re.IGNORECASE)
        if error_match:
            context.error_code = error_match.group(1) or error_match.group(2)
        
        # Determine safety level
        safety_keywords = {
            'critical': ['emergency', 'danger', 'critical', 'stop'],
            'high': ['safety', 'warning', 'caution', 'hazard'],
            'medium': ['maintenance', 'service', 'check'],
            'low': ['information', 'general', 'question']
        }
        
        query_lower = query.lower()
        for level, keywords in safety_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                context.safety_level = level
                break
        
        return context
    
    def classify_query(self, query: str) -> str:
        """Classify the type of manufacturing query"""
        query_lower = query.lower()
        
        for category, keywords in self.query_patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def search_knowledge_base(self, query: str, category: str, context: ManufacturingContext) -> str:
        """Search the pre-loaded knowledge base"""
        query_lower = query.lower()
        
        # Handle specific error codes
        if context.error_code and category == 'troubleshooting':
            error_code = context.error_code.upper()
            if error_code in self.knowledge_base['troubleshooting']['error_codes']:
                return self.knowledge_base['troubleshooting']['error_codes'][error_code]
        
        # Handle safety queries
        if category == 'safety':
            if 'lockout' in query_lower or 'tagout' in query_lower:
                return self.knowledge_base['safety_protocols']['lockout_tagout']
            elif 'emergency' in query_lower or 'stop' in query_lower:
                return self.knowledge_base['safety_protocols']['emergency_stop']
            elif 'ppe' in query_lower or 'protection' in query_lower:
                return self.knowledge_base['safety_protocols']['ppe_requirements']
        
        # Handle troubleshooting queries
        elif category == 'troubleshooting':
            if 'conveyor' in query_lower and 'noise' in query_lower:
                return self.knowledge_base['troubleshooting']['common_issues']['conveyor_noise']
            elif 'robot' in query_lower and ('not responding' in query_lower or 'unresponsive' in query_lower):
                return self.knowledge_base['troubleshooting']['common_issues']['robot_not_responding']
        
        # Handle maintenance queries
        elif category == 'maintenance':
            if 'cnc' in query_lower:
                return self.knowledge_base['maintenance']['schedules']['cnc_machine']
            elif 'conveyor' in query_lower:
                return self.knowledge_base['maintenance']['schedules']['conveyor_system']
        
        # Handle parts queries
        elif category == 'parts':
            if 'conveyor' in query_lower:
                return self.knowledge_base['parts_catalog']['conveyor_parts']
            elif 'cnc' in query_lower:
                return self.knowledge_base['parts_catalog']['cnc_parts']
        
        # Default response
        return """
I can help you with manufacturing questions about:

🚨 **Safety**: Lockout/tagout, emergency procedures, PPE requirements
🔧 **Troubleshooting**: Error codes (E001, E002), equipment issues
📋 **Maintenance**: Schedules for CNC machines, conveyor systems
📦 **Parts**: Part numbers and specifications

Try asking:
- "What is the lockout tagout procedure?"
- "Error code E001 troubleshooting"
- "Conveyor belt maintenance schedule"
- "Part number for conveyor belt"
"""
    
    def query(self, question: str) -> str:
        """Main query method for demo RAG"""
        # Extract context and classify query
        context = self.extract_context(question)
        category = self.classify_query(question)
        
        # Search knowledge base
        response = self.search_knowledge_base(question, category, context)
        
        # Add safety prefix for high-risk content
        if context.safety_level in ['critical', 'high']:
            response = "🚨 **SAFETY CRITICAL INFORMATION** 🚨\n\n" + response
        
        # Add context information if available
        if context.machine_id or context.error_code:
            context_info = []
            if context.machine_id:
                context_info.append(f"Machine: {context.machine_id}")
            if context.error_code:
                context_info.append(f"Error Code: {context.error_code}")
            
            response = f"**Context**: {', '.join(context_info)}\n\n" + response
        
        return response
    
    def test_demo(self):
        """Test the demo RAG with sample queries"""
        test_queries = [
            "What is the lockout tagout procedure?",
            "Machine error code E001 troubleshooting",
            "Conveyor belt making unusual noise",
            "CNC machine maintenance schedule",
            "Part number for conveyor belt",
            "Emergency stop procedure",
            "PPE requirements for welding area"
        ]
        
        print("🏭 Demo Manufacturing RAG Test")
        print("=" * 50)
        
        for query in test_queries:
            print(f"\n❓ Query: {query}")
            print("-" * 30)
            response = self.query(query)
            print(response)
            print()

# Example usage
if __name__ == "__main__":
    # Create demo client
    demo_rag = DemoManufacturingRAG()
    
    # Run test
    demo_rag.test_demo()
    
    # Interactive mode
    print("\n🎯 Interactive Demo Mode")
    print("Ask manufacturing questions (type 'quit' to exit):")
    
    while True:
        question = input("\n❓ Your question: ").strip()
        if question.lower() in ['quit', 'exit', 'q']:
            break
        
        if question:
            response = demo_rag.query(question)
            print(f"\n🤖 Response:\n{response}")