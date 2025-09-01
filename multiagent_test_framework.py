"""
Multi-Agent SBDR System Test Framework
Comprehensive testing for the Python-based multi-agent system.
"""

import asyncio
import unittest
import json
from typing import Dict, List
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the current directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multiagent_sbdr_system import (
    AgentOrchestrator, SBDRAgent, AccountManagerAgent, CustomerSuccessAgent,
    Intent, QualificationStatus, AgentType, UserProfile, Message, MessageType
)

class TestMultiAgentSystem(unittest.IsolatedAsyncioTestCase):
    """Test cases for the multi-agent SBDR system"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.orchestrator = AgentOrchestrator()
        self.test_knowledge_base = {
            "policies": {
                "shipping_policy": "Standard shipping takes 3-5 business days.",
                "return_policy": "30-day return policy for all products.",
                "warranty": "1-year warranty on all electronics."
            },
            "qualification_questions": {
                "budget_questions": ["What's your budget for this purchase?"],
                "use_case_questions": ["What will you primarily use this for?"],
                "product_questions": ["What type of product interests you most?"]
            },
            "common_responses": {
                "greeting": ["Hello! How can I help you today?", "Hi there! What can I assist you with?"]
            },
            "escalation_criteria": {
                "qualified_lead": {"budget_minimum": 500}
            }
        }
        
        # Update orchestrator's knowledge base
        self.orchestrator.knowledge_base = self.test_knowledge_base

    async def test_sbdr_agent_lead_qualification(self):
        """Test SBDR agent lead qualification process"""
        session_id = "test_session_1"
        
        # Test conversation flow
        messages = [
            "Hi, I'm looking for a laptop",
            "My budget is around $1500",
            "I need it for business work and presentations",
            "When can I get it delivered?"
        ]
        
        for i, message in enumerate(messages):
            result = await self.orchestrator.process_message(
                session_id=session_id,
                message_content=message,
                customer_tier="prospect"
            )
            
            # Verify SBDR agent is handling initial messages
            if i < 3:
                self.assertEqual(result['agent'], 'sbdr')
            
            # Verify qualification progression
            if i == 0:
                self.assertIn(result['user_profile']['qualification_status'], 
                            ['not_started', 'in_progress'])
            elif i == 2:  # After budget and use case provided
                self.assertIn(result['user_profile']['qualification_status'], 
                            ['completed', 'qualified'])
        
        # Check final profile
        profile = self.orchestrator.user_profiles[session_id]
        self.assertIsNotNone(profile.budget)
        self.assertIsNotNone(profile.use_case)
        self.assertGreater(profile.engagement_score, 0)

    async def test_agent_handoff_mechanism(self):
        """Test handoff between agents"""
        session_id = "test_handoff"
        
        # Start with SBDR qualification
        result1 = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="I'm looking for a laptop around $2000",
            customer_tier="prospect"
        )
        self.assertEqual(result1['agent'], 'sbdr')
        
        # Add more qualification data
        result2 = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="I need it for business presentations",
            customer_tier="prospect"
        )
        
        # Request human agent - should trigger handoff
        result3 = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="Can I speak to a human agent?",
            customer_tier="prospect"
        )
        
        # Should be handled by account manager now
        self.assertEqual(result3['agent'], 'account_manager')

    async def test_account_manager_customer_handling(self):
        """Test account manager handling existing customers"""
        session_id = "existing_customer"
        
        result = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="I need to check on my order status",
            user_name="John Doe",
            user_email="john@example.com",
            customer_tier="customer"
        )
        
        # Should route to account manager
        self.assertEqual(result['agent'], 'account_manager')
        self.assertEqual(result['intent'], 'order_status')
        self.assertIn('check_order_status', result['actions'])

    async def test_customer_success_agent(self):
        """Test customer success agent functionality"""
        session_id = "success_customer"
        
        result = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="I'd like to learn best practices for using my new device",
            user_name="Jane Smith",
            customer_tier="customer"
        )
        
        # Should route to customer success
        self.assertEqual(result['agent'], 'customer_success')
        self.assertIn('provide_best_practices', result['actions'])

    async def test_vip_customer_treatment(self):
        """Test VIP customer special handling"""
        session_id = "vip_customer"
        
        result = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="I'm interested in your premium products",
            user_name="VIP Customer",
            customer_tier="vip"
        )
        
        # Should route to account manager for VIP
        self.assertEqual(result['agent'], 'account_manager')
        self.assertIn('apply_vip_benefits', result['actions'])

    async def test_intent_detection_accuracy(self):
        """Test intent detection across different agents"""
        test_cases = [
            ("Hello there!", Intent.GREETING),
            ("I need a new laptop", Intent.PRODUCT_INQUIRY),
            ("What's the price?", Intent.PRICING),
            ("Where's my order?", Intent.ORDER_STATUS),
            ("I need help with my account", Intent.ACCOUNT_MANAGEMENT),
            ("Can you help me optimize my setup?", Intent.CUSTOMER_SUCCESS),
            ("I want to speak to a human", Intent.HANDOFF_REQUEST)
        ]
        
        sbdr_agent = self.orchestrator.agents[AgentType.SBDR]
        
        for message, expected_intent in test_cases:
            detected_intent = sbdr_agent.detect_intent(message)
            self.assertEqual(detected_intent, expected_intent, 
                           f"Failed for message: '{message}'")

    async def test_qualification_data_extraction(self):
        """Test extraction of qualification data"""
        sbdr_agent = self.orchestrator.agents[AgentType.SBDR]
        
        test_cases = [
            ("My budget is $1500", {"budget": "1500"}),
            ("I need it for business work", {"use_case": "business"}),
            ("Looking for gaming laptop under $2000", {"budget": "2000", "use_case": "gaming"}),
            ("I'm a student needing around $800", {"budget": "800", "use_case": "education"})
        ]
        
        for message, expected_data in test_cases:
            extracted = sbdr_agent.extract_qualification_data(message)
            for key, value in expected_data.items():
                self.assertIn(key, extracted)
                self.assertEqual(extracted[key], value)

    async def test_conversation_history_tracking(self):
        """Test conversation history and context preservation"""
        session_id = "history_test"
        
        messages = [
            "Hi, I need a laptop",
            "My budget is $1200",
            "What are my options?"
        ]
        
        for message in messages:
            await self.orchestrator.process_message(
                session_id=session_id,
                message_content=message
            )
        
        # Check conversation history
        profile = self.orchestrator.user_profiles[session_id]
        self.assertEqual(len(profile.conversation_history), 3)
        
        # Check session conversation
        session_history = self.orchestrator.conversation_history[session_id]
        self.assertEqual(len(session_history), 6)  # 3 user messages + 3 agent responses

    async def test_concurrent_sessions(self):
        """Test handling multiple concurrent sessions"""
        sessions = ["session_1", "session_2", "session_3"]
        messages = [
            "Hi, looking for phones",
            "Need laptops for office",
            "Gaming setup advice please"
        ]
        
        # Process messages concurrently
        tasks = []
        for i, session_id in enumerate(sessions):
            task = self.orchestrator.process_message(
                session_id=session_id,
                message_content=messages[i],
                customer_tier="prospect" if i < 2 else "customer"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Verify each session was handled independently
        self.assertEqual(len(results), 3)
        self.assertEqual(len(self.orchestrator.user_profiles), 3)
        
        # Verify different agents were selected based on customer tier
        self.assertEqual(results[0]['agent'], 'sbdr')  # prospect
        self.assertEqual(results[1]['agent'], 'sbdr')  # prospect
        # Customer success could handle the gaming advice
        self.assertIn(results[2]['agent'], ['customer_success', 'account_manager'])

    async def test_knowledge_base_queries(self):
        """Test knowledge base querying functionality"""
        sbdr_agent = self.orchestrator.agents[AgentType.SBDR]
        
        test_queries = [
            ("What's your shipping policy?", "shipping"),
            ("Tell me about returns", "return"),
            ("What about warranty?", "warranty")
        ]
        
        for query, policy_type in test_queries:
            response = sbdr_agent._query_knowledge_base(query)
            self.assertIsNotNone(response)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 10)

    async def test_agent_selection_logic(self):
        """Test the agent selection mechanism"""
        # Create different user profiles
        prospect_profile = UserProfile(
            session_id="prospect",
            customer_tier="prospect",
            qualification_status=QualificationStatus.IN_PROGRESS
        )
        
        customer_profile = UserProfile(
            session_id="customer",
            customer_tier="customer"
        )
        
        vip_profile = UserProfile(
            session_id="vip",
            customer_tier="vip"
        )
        
        # Test agent selection for different scenarios
        test_cases = [
            (Intent.GREETING, prospect_profile, AgentType.SBDR),
            (Intent.PRODUCT_INQUIRY, prospect_profile, AgentType.SBDR),
            (Intent.ORDER_STATUS, customer_profile, AgentType.ACCOUNT_MANAGER),
            (Intent.CUSTOMER_SUCCESS, customer_profile, AgentType.CUSTOMER_SUCCESS),
            (Intent.ACCOUNT_MANAGEMENT, vip_profile, AgentType.ACCOUNT_MANAGER)
        ]
        
        for intent, profile, expected_agent_type in test_cases:
            selected_agent = self.orchestrator._select_agent(intent, profile)
            self.assertEqual(selected_agent.agent_type, expected_agent_type)

    async def test_conversation_summary_generation(self):
        """Test conversation summary functionality"""
        session_id = "summary_test"
        
        # Have a conversation
        messages = [
            "Hello, I'm looking for a laptop",
            "My budget is around $1800",
            "I need it for video editing work"
        ]
        
        for message in messages:
            await self.orchestrator.process_message(
                session_id=session_id,
                message_content=message,
                user_name="Test User"
            )
        
        # Get summary
        summary = self.orchestrator.get_conversation_summary(session_id)
        
        self.assertIn('session_id', summary)
        self.assertIn('conversation_length', summary)
        self.assertIn('agents_involved', summary)
        self.assertIn('intents_detected', summary)
        self.assertGreater(summary['conversation_length'], 0)

class TestIntegrationScenarios(unittest.IsolatedAsyncioTestCase):
    """Test realistic end-to-end scenarios"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        self.orchestrator = AgentOrchestrator()

    async def test_complete_prospect_journey(self):
        """Test complete prospect to customer journey"""
        session_id = "prospect_journey"
        
        # Initial inquiry
        result1 = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="Hi, I'm looking for a laptop for my business",
            user_name="Business Owner"
        )
        self.assertEqual(result1['agent'], 'sbdr')
        
        # Qualification
        result2 = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="My budget is around $2500 and I need it for presentations and spreadsheets"
        )
        
        # Request for specific models
        result3 = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="Can someone show me specific models in that range?"
        )
        
        # Should handoff to account manager
        profile = self.orchestrator.user_profiles[session_id]
        self.assertIn(profile.qualification_status, 
                     [QualificationStatus.QUALIFIED, QualificationStatus.COMPLETED])

    async def test_existing_customer_support_flow(self):
        """Test existing customer support interaction"""
        session_id = "customer_support"
        
        # Customer with account issue
        result1 = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="I'm having trouble with my recent order",
            user_name="John Customer",
            user_email="john@customer.com",
            customer_tier="customer"
        )
        self.assertEqual(result1['agent'], 'account_manager')
        
        # Follow up with onboarding question
        result2 = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="Also, can you help me set up my new device optimally?"
        )
        
        # Might stay with account manager or move to customer success
        self.assertIn(result2['agent'], ['account_manager', 'customer_success'])

    async def test_vip_customer_experience(self):
        """Test VIP customer premium experience"""
        session_id = "vip_experience"
        
        result = await self.orchestrator.process_message(
            session_id=session_id,
            message_content="I'm interested in your latest premium products",
            user_name="VIP Customer",
            customer_tier="vip"
        )
        
        # Should go to account manager
        self.assertEqual(result['agent'], 'account_manager')
        self.assertIn('apply_vip_benefits', result['actions'])

def run_performance_tests():
    """Run performance tests for the multi-agent system"""
    import time
    
    async def performance_test():
        orchestrator = AgentOrchestrator()
        
        # Test response time
        start_time = time.time()
        await orchestrator.process_message(
            session_id="perf_test",
            message_content="I'm looking for a laptop under $1000"
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"Single message response time: {response_time:.3f}s")
        assert response_time < 0.1, f"Response time too slow: {response_time}s"
        
        # Test concurrent processing
        start_time = time.time()
        tasks = []
        for i in range(10):
            task = orchestrator.process_message(
                session_id=f"concurrent_{i}",
                message_content=f"Message {i}: I need help with products"
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        concurrent_time = end_time - start_time
        print(f"10 concurrent messages time: {concurrent_time:.3f}s")
        assert concurrent_time < 1.0, f"Concurrent processing too slow: {concurrent_time}s"
        
        print("✅ Performance tests passed!")
    
    asyncio.run(performance_test())

def run_example_conversations():
    """Run example conversations to demonstrate the system"""
    
    async def demo_conversations():
        print("\n" + "="*60)
        print("MULTI-AGENT SBDR SYSTEM DEMONSTRATION")
        print("="*60)
        
        orchestrator = AgentOrchestrator()
        
        scenarios = [
            {
                "name": "New Prospect - Laptop Shopping",
                "session_id": "demo_prospect",
                "customer_tier": "prospect",
                "user_name": "Sarah Johnson",
                "messages": [
                    "Hi, I'm looking for a laptop for work",
                    "My budget is around $1800",
                    "I need it for design work and presentations",
                    "Can someone help me with specific recommendations?"
                ]
            },
            {
                "name": "Existing Customer - Order Support",
                "session_id": "demo_customer", 
                "customer_tier": "customer",
                "user_name": "Mike Chen",
                "messages": [
                    "I need to check on my order from last week",
                    "Also, I'm having trouble setting up the software",
                    "Can you help me optimize the settings?"
                ]
            },
            {
                "name": "VIP Customer - Premium Service",
                "session_id": "demo_vip",
                "customer_tier": "vip", 
                "user_name": "Executive Client",
                "messages": [
                    "I'm interested in your latest enterprise solutions",
                    "What premium support options do you offer?",
                    "I'd like to schedule a consultation"
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"\n{'='*60}")
            print(f"SCENARIO: {scenario['name']}")
            print(f"Customer: {scenario['user_name']} ({scenario['customer_tier']})")
            print(f"{'='*60}")
            
            for i, message in enumerate(scenario['messages']):
                result = await orchestrator.process_message(
                    session_id=scenario['session_id'],
                    message_content=message,
                    user_name=scenario['user_name'],
                    customer_tier=scenario['customer_tier']
                )
                
                print(f"\n👤 Customer: {message}")
                print(f"🤖 {result['agent'].title()} Agent: {result['response']}")
                print(f"📊 Intent: {result['intent']} | Actions: {result['actions']}")
                print(f"📈 Status: {result['user_profile']['qualification_status']} | Score: {result['user_profile']['engagement_score']}")
                
                if 'handoff_occurred' in result['metadata']:
                    print(f"🔄 Handoff from {result['metadata']['previous_agent']} to {result['agent']}")
                
                print("-" * 40)
            
            # Show final conversation summary
            summary = orchestrator.get_conversation_summary(scenario['session_id'])
            print(f"\n📋 Conversation Summary:")
            print(f"   Messages: {summary['conversation_length']}")
            print(f"   Agents: {summary['agents_involved']}")
            print(f"   Intents: {summary['intents_detected']}")
    
    asyncio.run(demo_conversations())

if __name__ == "__main__":
    print("Multi-Agent SBDR System Test Framework")
    print("=" * 50)
    
    # Run unit tests
    print("\n🧪 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    print("\n⚡ Running Performance Tests...")
    run_performance_tests()
    
    # Run example conversations
    print("\n🎭 Running Example Conversations...")
    run_example_conversations()
    
    print("\n✅ All tests completed!")