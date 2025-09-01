# Multi-Agent SBDR System

A Python-based multi-agent system for sales, account management, and customer success built on the architecture from the existing SBDR project but running natively in Python instead of N8N.

## 🏗️ System Architecture

The multi-agent system employs a sophisticated orchestration layer that routes conversations between specialized agents based on customer context, intent, and business rules.

### Agent Types

1. **SBDR Agent** - Handles initial lead qualification and prospect engagement
2. **Account Manager Agent** - Manages qualified leads and existing customers  
3. **Customer Success Agent** - Provides ongoing support and value optimization

### Key Components

- **Agent Orchestrator** - Central routing and coordination system
- **Integration Layer** - Connects to Crisp, Shopify, and OpenAI APIs
- **User Profile Management** - Maintains conversation context and qualification status
- **Intelligent Handoffs** - Dynamic agent selection based on customer needs

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from multiagent_sbdr_system import AgentOrchestrator

async def main():
    orchestrator = AgentOrchestrator()
    
    result = await orchestrator.process_message(
        session_id="demo_session",
        message_content="I'm looking for a laptop for business use",
        user_name="John Doe",
        customer_tier="prospect"
    )
    
    print(f"Agent: {result['agent']}")
    print(f"Response: {result['response']}")

asyncio.run(main())
```

### With Integrations

```python
from run_multiagent_demo import EnhancedSBDROrchestrator

async def main():
    orchestrator = EnhancedSBDROrchestrator()
    await orchestrator.initialize_integrations()
    
    result = await orchestrator.process_message_enhanced(
        session_id="enhanced_session",
        message_content="What laptops do you have under $1500?",
        user_name="Jane Smith"
    )

asyncio.run(main())
```

## 📁 File Structure

```
├── multiagent_sbdr_system.py      # Core multi-agent system
├── multiagent_integrations.py     # External service integrations
├── multiagent_test_framework.py   # Comprehensive testing suite
├── run_multiagent_demo.py         # Complete demo and examples
└── MULTIAGENT_README.md            # This file
```

## 🧪 Running Tests

### Unit Tests
```bash
python multiagent_test_framework.py
```

### Integration Tests  
```bash
python multiagent_integrations.py
```

### Full Demo
```bash
python run_multiagent_demo.py
```

## 🔧 Configuration

### Environment Variables

```bash
# OpenAI Integration
OPENAI_API_KEY=your_openai_api_key_here

# Crisp Integration
CRISP_IDENTIFIER=your_crisp_identifier
CRISP_KEY=your_crisp_api_key
CRISP_WEBSITE_ID=your_website_id

# Shopify Integration  
SHOPIFY_SHOP_DOMAIN=your-shop-name
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
```

### Knowledge Base Configuration

The system uses `knowledge_base.json` for:
- FAQ responses and policies
- Qualification questions
- Product categories and information
- Escalation criteria

## 🤖 Agent Capabilities

### SBDR Agent
- Intent detection and classification
- Lead qualification through conversational flow
- Budget and requirement extraction
- Qualification question generation
- Handoff decision making

### Account Manager Agent
- Qualified lead handling
- Customer account management
- Order status and support
- VIP customer premium service
- Product recommendations

### Customer Success Agent  
- Customer onboarding assistance
- Best practices education
- Usage optimization guidance
- Retention workflow management
- Health score calculation

## 🔄 Agent Selection Logic

The orchestrator selects agents based on:

1. **Customer Tier** (prospect, customer, vip)
2. **Intent Classification** (greeting, product inquiry, support, etc.)
3. **Qualification Status** (not started, in progress, qualified, etc.)
4. **Conversation Context** (agent capabilities, handoff requests)

### Selection Priority

1. Account Manager - for qualified leads and existing customers
2. Customer Success - for customer education and optimization
3. SBDR Agent - default for prospects and qualification

## 📊 Analytics and Tracking

### User Profile Tracking
- Qualification status progression
- Engagement score calculation  
- Conversation history maintenance
- Agent interaction tracking

### Conversation Analytics
- Intent classification accuracy
- Agent usage statistics
- Handoff frequency and success
- Customer journey mapping

### Business Metrics
- Lead qualification rates
- Agent response times
- Customer satisfaction indicators
- Conversion tracking

## 🔗 Integration Features

### Crisp Chat Integration
- Real-time message sending
- Conversation metadata access
- State management (resolved/unresolved)
- Multi-channel support

### Shopify E-commerce Integration
- Product search and recommendations
- Customer order history
- Inventory status checking
- Customer profile access

### OpenAI Integration
- Agent-specific response generation
- Context-aware prompting
- Conversation quality enhancement
- Multi-model support

## 🧪 Testing Framework

### Test Categories

1. **Unit Tests** - Individual agent functionality
2. **Integration Tests** - Agent handoffs and workflows
3. **End-to-End Tests** - Complete customer journeys
4. **Performance Tests** - Response times and concurrency
5. **Integration Tests** - External service connectivity

### Example Test Scenarios

- New prospect qualification journey
- Existing customer support interaction
- VIP customer premium service
- Complex multi-agent handoffs
- Concurrent session handling

## 🎯 Key Features

### Intelligent Agent Orchestration
- Dynamic agent selection based on context
- Seamless handoffs between specialized agents
- Conversation context preservation
- Business rule-based routing

### Advanced Lead Qualification
- Multi-factor qualification scoring
- Progressive information gathering
- Context-aware question generation
- Automatic qualification status updates

### Customer Journey Management
- Session-based conversation tracking
- Engagement score calculation
- Customer tier-based service levels
- Comprehensive conversation history

### Real-time Integration Capabilities
- Live product recommendations
- AI-enhanced response generation
- External system synchronization
- Multi-platform message delivery

## 🚀 Advanced Usage

### Custom Agent Development

```python
from multiagent_sbdr_system import BaseAgent, AgentType, Intent

class CustomAgent(BaseAgent):
    def __init__(self, knowledge_base):
        super().__init__(AgentType.CUSTOM, knowledge_base)
    
    def can_handle(self, intent, user_profile):
        # Custom handling logic
        return intent == Intent.CUSTOM_INTENT
    
    async def process_message(self, message, user_profile):
        # Custom processing logic
        return AgentResponse(...)
```

### Integration Extension

```python
from multiagent_integrations import BaseIntegration

class CustomIntegration(BaseIntegration):
    async def test_connection(self):
        # Connection test logic
        return True
    
    async def custom_operation(self, data):
        # Custom integration logic
        return result
```

### Performance Optimization

```python
# Concurrent session handling
tasks = []
for session in sessions:
    task = orchestrator.process_message(...)
    tasks.append(task)

results = await asyncio.gather(*tasks)
```

## 🔍 Monitoring and Debugging

### Logging Configuration
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

### Conversation Analysis
```python
summary = orchestrator.get_conversation_summary(session_id)
print(f"Messages: {summary['conversation_length']}")
print(f"Agents: {summary['agents_involved']}")
```

### Performance Monitoring
```python
import time
start_time = time.time()
result = await orchestrator.process_message(...)
response_time = time.time() - start_time
```

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install aiohttp asyncio`
3. Configure environment variables
4. Run tests: `python multiagent_test_framework.py`

### Code Standards
- Follow existing patterns for agent development
- Add comprehensive tests for new features
- Update documentation for API changes
- Maintain backward compatibility

## 📈 Roadmap

### Planned Features
- Additional specialized agents (Technical Support, Sales Engineering)
- Advanced analytics dashboard
- Real-time conversation monitoring
- Machine learning-based intent improvement
- Multi-language support

### Integration Expansions
- Slack and Teams integration
- CRM system connectivity (Salesforce, HubSpot)
- Voice channel support
- Social media platform integration

## 📄 License

This project builds upon the existing SBDR system architecture and maintains compatibility with the original N8N-based implementation while providing enhanced Python-native capabilities.

## 🆘 Support

For questions and support:
1. Check the comprehensive test framework for usage examples
2. Review the demo scenarios in `run_multiagent_demo.py`
3. Examine the integration examples in `multiagent_integrations.py`
4. Run the test suite for system validation