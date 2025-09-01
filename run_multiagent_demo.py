"""
Multi-Agent SBDR System - Complete Demo
Demonstrates the full multi-agent system with integrations and realistic scenarios.
"""

import asyncio
import json
import os
import logging
from typing import Dict, Any

# Import our multi-agent system components
from multiagent_sbdr_system import AgentOrchestrator, AgentType, QualificationStatus
from multiagent_integrations import (
    IntegrationManager, CrispConfig, ShopifyConfig, OpenAIConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedSBDROrchestrator(AgentOrchestrator):
    """Enhanced orchestrator with integration capabilities"""
    
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        super().__init__(knowledge_base_path)
        self.integration_manager = IntegrationManager()
        self.ai_enabled = False
        self.integrations_ready = False
    
    async def initialize_integrations(self, use_mock_data: bool = True):
        """Initialize integrations (with mock data option for demo)"""
        if use_mock_data:
            # Use mock configurations for demo
            logger.info("Initializing with mock integrations for demo...")
            await self._initialize_mock_integrations()
        else:
            # Use real integrations from environment
            logger.info("Initializing real integrations from environment...")
            await self.integration_manager.initialize_from_env()
        
        # Test connections
        test_results = await self.integration_manager.test_all_connections()
        self.integrations_ready = any(test_results.values())
        
        logger.info(f"Integration status: {test_results}")
    
    async def _initialize_mock_integrations(self):
        """Initialize with mock configurations for demo purposes"""
        # Mock Crisp config
        crisp_config = CrispConfig(
            identifier="mock_id",
            key="mock_key", 
            website_id="mock_website_id"
        )
        
        # Mock Shopify config
        shopify_config = ShopifyConfig(
            shop_domain="demo-store",
            access_token="mock_token"
        )
        
        # Real OpenAI config if available
        openai_key = os.getenv("OPENAI_API_KEY")
        openai_config = OpenAIConfig(api_key=openai_key) if openai_key else None
        
        await self.integration_manager.initialize(
            crisp_config=crisp_config,
            shopify_config=shopify_config, 
            openai_config=openai_config
        )
    
    async def process_message_enhanced(self, session_id: str, message_content: str,
                                     user_name: str = "Guest", 
                                     user_email: str = None,
                                     customer_tier: str = "prospect") -> Dict[str, Any]:
        """Enhanced message processing with AI and product integration"""
        
        # Get base response from multi-agent system
        result = await self.process_message(
            session_id=session_id,
            message_content=message_content,
            user_name=user_name,
            user_email=user_email,
            customer_tier=customer_tier
        )
        
        # Enhance response with AI if available
        if self.integration_manager.openai:
            try:
                user_profile = self.user_profiles[session_id]
                context = {
                    "customer_tier": user_profile.customer_tier,
                    "qualification_status": user_profile.qualification_status.value,
                    "budget": user_profile.budget,
                    "product_interest": user_profile.product_interest
                }
                
                ai_response = await self.integration_manager.generate_ai_response(
                    agent_type=result['agent'],
                    message=message_content,
                    context=context
                )
                
                if ai_response:
                    result['response'] = ai_response
                    result['ai_enhanced'] = True
                
            except Exception as e:
                logger.warning(f"AI enhancement failed: {e}")
        
        # Add product recommendations if relevant
        if result['intent'] in ['product_inquiry', 'pricing'] and self.integration_manager.shopify:
            try:
                user_profile = self.user_profiles[session_id]
                if user_profile.product_interest:
                    products = await self.integration_manager.search_products(
                        query="",  # Search all
                        product_type=user_profile.product_interest
                    )
                    
                    if products:
                        result['product_recommendations'] = products[:3]
                        
                        # Add products to response
                        product_text = "\n\nHere are some products that might interest you:\n"
                        for i, product in enumerate(products[:3], 1):
                            product_text += f"{i}. {product['title']} - ${product['price']}\n"
                        
                        result['response'] += product_text
                        
            except Exception as e:
                logger.warning(f"Product search failed: {e}")
        
        # Send to Crisp if configured (mock for demo)
        if self.integration_manager.crisp:
            try:
                await self.integration_manager.send_message_to_crisp(
                    session_id=session_id,
                    message=result['response']
                )
                result['sent_to_crisp'] = True
            except Exception as e:
                logger.warning(f"Crisp integration failed: {e}")
        
        return result

async def run_comprehensive_demo():
    """Run comprehensive multi-agent demo scenarios"""
    
    print("\n" + "="*80)
    print("🚀 MULTI-AGENT SBDR SYSTEM - COMPREHENSIVE DEMO")
    print("="*80)
    
    # Initialize enhanced orchestrator
    orchestrator = EnhancedSBDROrchestrator()
    await orchestrator.initialize_integrations(use_mock_data=True)
    
    # Demo scenarios
    scenarios = [
        {
            "name": "🔍 New Prospect - Complete Qualification Journey",
            "session_id": "prospect_journey_2024",
            "customer_data": {
                "user_name": "Alex Martinez",
                "user_email": "alex@startup.com",
                "customer_tier": "prospect"
            },
            "conversation": [
                "Hi! I'm looking for laptops for my growing startup team",
                "We need about 5 laptops, budget is around $8000 total",
                "They'll be used for software development and design work",
                "What are the best options in that range?",
                "Can someone help me with bulk pricing and setup?"
            ]
        },
        {
            "name": "📦 Existing Customer - Order & Support",
            "session_id": "customer_support_2024",
            "customer_data": {
                "user_name": "Jennifer Chen",
                "user_email": "jennifer@company.com", 
                "customer_tier": "customer"
            },
            "conversation": [
                "Hello! I need to check on my order from last week",
                "Order #12345 - it was supposed to arrive yesterday",
                "Also, I'm having trouble with the initial setup of my new laptop",
                "Can you help me optimize the performance settings?",
                "I'd like to learn about best practices for maintenance"
            ]
        },
        {
            "name": "⭐ VIP Customer - Premium Service Experience", 
            "session_id": "vip_experience_2024",
            "customer_data": {
                "user_name": "Executive David Kim",
                "user_email": "dkim@enterprise.com",
                "customer_tier": "vip"
            },
            "conversation": [
                "Good morning! I'm interested in your latest enterprise workstations",
                "I need high-end machines for our executive team - performance is critical",
                "What premium support and services do you offer?",
                "I'd like to discuss a long-term partnership arrangement"
            ]
        },
        {
            "name": "🔄 Agent Handoff - Complex Inquiry",
            "session_id": "complex_handoff_2024", 
            "customer_data": {
                "user_name": "Tech Lead Sarah Johnson",
                "user_email": "sarah@techcorp.com",
                "customer_tier": "prospect"
            },
            "conversation": [
                "Hi, I need advice on building a complete development environment",
                "Budget is flexible, probably $15k-20k for the full setup",
                "We need workstations, monitors, networking equipment - everything",
                "This is quite complex - can I speak with a technical specialist?",
                "I'd also like ongoing support for the team once it's set up"
            ]
        }
    ]
    
    # Run each scenario
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"{scenario['name']}")
        print(f"Customer: {scenario['customer_data']['user_name']} ({scenario['customer_data']['customer_tier']})")
        print(f"{'='*80}")
        
        conversation_summary = {
            "agents_used": set(),
            "handoffs": [],
            "qualification_progression": [],
            "key_insights": []
        }
        
        for i, message in enumerate(scenario['conversation']):
            print(f"\n💬 Message {i+1}: {message}")
            
            # Process message with enhanced orchestrator
            result = await orchestrator.process_message_enhanced(
                session_id=scenario['session_id'],
                message_content=message,
                **scenario['customer_data']
            )
            
            # Display response
            print(f"🤖 {result['agent'].title().replace('_', ' ')} Agent:")
            print(f"   {result['response']}")
            
            # Show system information
            print(f"📊 System Info:")
            print(f"   Intent: {result['intent']} | Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Qualification: {result['user_profile']['qualification_status']}")
            print(f"   Engagement Score: {result['user_profile']['engagement_score']}")
            
            if result.get('actions'):
                print(f"   Actions: {', '.join(result['actions'])}")
            
            # Track conversation analytics
            conversation_summary["agents_used"].add(result['agent'])
            conversation_summary["qualification_progression"].append(
                result['user_profile']['qualification_status']
            )
            
            if result.get('metadata', {}).get('handoff_occurred'):
                conversation_summary["handoffs"].append({
                    "from": result['metadata']['previous_agent'],
                    "to": result['agent'],
                    "message": i+1
                })
            
            # Show additional features
            if result.get('ai_enhanced'):
                print(f"   ✨ AI Enhanced Response")
            
            if result.get('product_recommendations'):
                print(f"   🛍️ Product Recommendations: {len(result['product_recommendations'])} items")
            
            if result.get('sent_to_crisp'):
                print(f"   📨 Sent to Crisp Chat")
            
            print("-" * 60)
        
        # Show conversation analytics
        print(f"\n📈 CONVERSATION ANALYTICS:")
        print(f"   Agents Used: {', '.join(conversation_summary['agents_used'])}")
        print(f"   Handoffs: {len(conversation_summary['handoffs'])}")
        
        for handoff in conversation_summary['handoffs']:
            print(f"      Message {handoff['message']}: {handoff['from']} → {handoff['to']}")
        
        # Show final user profile
        profile = orchestrator.user_profiles[scenario['session_id']]
        print(f"\n👤 FINAL USER PROFILE:")
        print(f"   Name: {profile.name}")
        print(f"   Qualification Status: {profile.qualification_status.value}")
        print(f"   Budget: {profile.budget or 'Not specified'}")
        print(f"   Product Interest: {profile.product_interest or 'Not specified'}")
        print(f"   Use Case: {profile.use_case or 'Not specified'}")
        print(f"   Engagement Score: {profile.engagement_score}")
        print(f"   Current Agent: {profile.current_agent.value if profile.current_agent else 'None'}")
        
        # Business insights
        print(f"\n💼 BUSINESS INSIGHTS:")
        if profile.qualification_status == QualificationStatus.QUALIFIED:
            print(f"   ✅ QUALIFIED LEAD - Ready for sales team")
        elif profile.qualification_status == QualificationStatus.COMPLETED:
            print(f"   ⚠️ Completed but needs review")
        else:
            print(f"   🔄 Still in qualification process")
        
        if profile.customer_tier == "vip":
            print(f"   ⭐ VIP Customer - Premium service provided")
        
        if profile.engagement_score > 5:
            print(f"   🔥 High engagement - Strong prospect")
    
    # Overall system statistics
    print(f"\n{'='*80}")
    print("📊 SYSTEM PERFORMANCE SUMMARY")
    print(f"{'='*80}")
    print(f"Total Sessions: {len(orchestrator.user_profiles)}")
    print(f"Total Messages Processed: {sum(len(h) for h in orchestrator.conversation_history.values())}")
    print(f"Agents Available: {len(orchestrator.agents)}")
    print(f"Integration Status: {'✅ Connected' if orchestrator.integrations_ready else '❌ Mock Mode'}")
    
    # Agent usage statistics
    agent_usage = {}
    for session_history in orchestrator.conversation_history.values():
        for message in session_history:
            if hasattr(message, 'sender') and 'agent' in message.sender:
                agent = message.sender.replace('_agent', '')
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
    
    print(f"\n🤖 Agent Usage:")
    for agent, count in agent_usage.items():
        print(f"   {agent.title()}: {count} responses")
    
    print(f"\n✅ Demo completed successfully!")

async def run_integration_tests():
    """Test the integration layer specifically"""
    print("\n" + "="*60)
    print("🔧 INTEGRATION LAYER TESTING")
    print("="*60)
    
    integration_manager = IntegrationManager()
    
    # Test with environment variables
    await integration_manager.initialize_from_env()
    
    # Test connections
    results = await integration_manager.test_all_connections()
    print(f"\n🔌 Connection Tests:")
    for service, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"   {service.title()}: {status}")
    
    # Test mock product search
    print(f"\n🔍 Testing Mock Product Search:")
    if integration_manager.shopify:
        products = await integration_manager.search_products("laptop")
        print(f"   Found {len(products)} products")
    else:
        print("   Shopify not configured - using mock data")
        # Simulate mock products
        mock_products = [
            {"title": "MacBook Pro 16\"", "price": "2499", "vendor": "Apple"},
            {"title": "ThinkPad X1 Carbon", "price": "1899", "vendor": "Lenovo"},
            {"title": "Dell XPS 15", "price": "1999", "vendor": "Dell"}
        ]
        print(f"   Mock products: {len(mock_products)} items")
        for product in mock_products:
            print(f"      - {product['title']} by {product['vendor']}: ${product['price']}")

if __name__ == "__main__":
    print("🚀 Starting Multi-Agent SBDR System Demo...")
    
    # Run the comprehensive demo
    asyncio.run(run_comprehensive_demo())
    
    # Run integration tests
    asyncio.run(run_integration_tests())
    
    print(f"\n🎉 All demos completed! Check the output above for detailed interactions.")