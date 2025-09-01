# SBDR Multi-Agent System - Information Flow Diagram

```mermaid
graph TD
    %% External Interfaces
    USER[👤 User/Customer] --> WEB[🌐 Web Interface<br/>FastAPI + WebSocket]
    CRISP[💬 Crisp Chat] --> WEB
    
    %% Main System Components
    WEB --> ORCHESTRATOR[🎯 Agent Orchestrator<br/>- Message routing<br/>- Agent selection<br/>- State management]
    
    %% Agent Layer
    ORCHESTRATOR --> SBDR[🤖 SBDR Agent<br/>- Lead qualification<br/>- Initial engagement<br/>- Product inquiry]
    ORCHESTRATOR --> ACCOUNT[👔 Account Manager<br/>- Order status<br/>- Product recommendations<br/>- Customer history]
    ORCHESTRATOR --> SUCCESS[⭐ Customer Success<br/>- Onboarding<br/>- Best practices<br/>- Health tracking]
    
    %% Integration Layer
    SBDR --> INTEGRATIONS[🔌 Integration Manager]
    ACCOUNT --> INTEGRATIONS
    SUCCESS --> INTEGRATIONS
    
    INTEGRATIONS --> OPENAI[🧠 OpenAI API<br/>- Natural language<br/>- Response generation]
    INTEGRATIONS --> SHOPIFY[🛍️ Shopify API<br/>- Product data<br/>- Order management]
    INTEGRATIONS --> CRISP_API[💬 Crisp API<br/>- Chat management<br/>- Message routing]
    
    %% Data Storage
    ORCHESTRATOR --> POSTGRES[(🗄️ PostgreSQL<br/>- Conversation history<br/>- User profiles<br/>- Analytics)]
    ORCHESTRATOR --> REDIS[(⚡ Redis Cache<br/>- Session data<br/>- Temporary state)]
    ORCHESTRATOR --> KB[📚 Knowledge Base<br/>JSON file with:<br/>- Product info<br/>- Policies<br/>- FAQs]
    
    %% Monitoring & Analytics
    WEB --> METRICS[📊 Metrics Endpoint<br/>- Agent usage<br/>- Performance stats<br/>- Qualification data]
    
    %% Information Flow Details
    subgraph "Message Processing Flow"
        MSG1[1. Message Received] --> INTENT[2. Intent Classification<br/>- Greeting<br/>- Product inquiry<br/>- Support<br/>- Order status]
        INTENT --> AGENT_SELECT[3. Agent Selection<br/>Based on:<br/>- Intent type<br/>- Customer tier<br/>- Current context]
        AGENT_SELECT --> PROCESS[4. Agent Processing<br/>- Generate response<br/>- Update profile<br/>- Log interactions]
        PROCESS --> RESPONSE[5. Response Delivery<br/>- Format message<br/>- Send to user<br/>- Update metrics]
    end
    
    %% User Profile Management
    subgraph "User Profile System"
        PROFILE[👤 User Profile] --> QUALIFICATION[📋 Qualification Status<br/>- not_started<br/>- in_progress<br/>- qualified<br/>- unqualified]
        PROFILE --> ENGAGEMENT[📈 Engagement Score<br/>- Message count<br/>- Response quality<br/>- Time spent]
        PROFILE --> CUSTOMER_TIER[🏷️ Customer Tier<br/>- prospect<br/>- customer<br/>- vip]
    end
    
    %% Data Flow Paths
    style USER fill:#e1f5fe
    style WEB fill:#f3e5f5
    style ORCHESTRATOR fill:#fff3e0
    style SBDR fill:#e8f5e8
    style ACCOUNT fill:#e8f5e8
    style SUCCESS fill:#e8f5e8
    style POSTGRES fill:#fce4ec
    style REDIS fill:#fff8e1
    style OPENAI fill:#e3f2fd
    style SHOPIFY fill:#f1f8e9
    style CRISP_API fill:#fce4ec
```

## Key Information Flows

### 1. **Inbound Message Flow**
```
User Message → Web Interface → Orchestrator → Intent Analysis → Agent Selection → Response Generation
```

### 2. **Agent Decision Flow**
```mermaid
flowchart LR
    INTENT[Intent Detected] --> ROUTING{Routing Logic}
    
    ROUTING -->|greeting, product_inquiry| SBDR_AGENT[SBDR Agent]
    ROUTING -->|order_status, recommendations| ACCOUNT_AGENT[Account Manager]
    ROUTING -->|customer_success, onboarding| SUCCESS_AGENT[Customer Success]
    
    SBDR_AGENT --> QUALIFY[Lead Qualification]
    ACCOUNT_AGENT --> ORDER[Order Management]
    SUCCESS_AGENT --> HEALTH[Customer Health]
```

### 3. **Data Persistence Flow**
```
Agent Response → User Profile Update → Conversation History → Database Storage → Analytics
```

### 4. **Integration Data Flow**
- **OpenAI**: Natural language processing and response generation
- **Shopify**: Product data retrieval and order information
- **Crisp**: External chat platform integration
- **Knowledge Base**: Static information lookup (policies, FAQs, product details)

### 5. **Real-time Communication**
```
WebSocket Connection → Live Chat → Immediate Response → State Synchronization
```

## Agent Specialization

| Agent | Primary Function | Key Data Sources | Outputs |
|-------|-----------------|------------------|----------|
| **SBDR** | Lead qualification, initial engagement | Knowledge base, user input | Qualification status, engagement score |
| **Account Manager** | Order management, product recommendations | Shopify API, user history | Order updates, product suggestions |
| **Customer Success** | Onboarding, best practices, health tracking | User profile, interaction history | Success metrics, health scores |

## Data Storage Strategy

- **PostgreSQL**: Persistent conversation history, user profiles, analytics
- **Redis**: Session caching, temporary state, real-time data
- **Knowledge Base JSON**: Static reference data for quick lookup
- **In-memory**: Current conversation context, agent state

## Monitoring & Analytics

The system tracks:
- Agent usage statistics
- Qualification conversion rates
- Response times
- User engagement metrics
- System health indicators

This architecture ensures scalable, maintainable multi-agent conversations with proper data flow and state management.