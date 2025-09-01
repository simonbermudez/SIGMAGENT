"""
Multi-Agent SBDR System
A Python-based multi-agent system for sales, account management, and customer success.
Built on the architecture from the existing SBDR project but with native Python agents.
"""

import json
import uuid
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime
import re
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enums from the original project
class Intent(Enum):
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    PRICING = "pricing"
    ORDER_STATUS = "order_status"
    SHIPPING = "shipping"
    SUPPORT = "support"
    HANDOFF_REQUEST = "handoff_request"
    QUALIFICATION_RESPONSE = "qualification_response"
    ACCOUNT_MANAGEMENT = "account_management"
    CUSTOMER_SUCCESS = "customer_success"
    GENERAL = "general"

class QualificationStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"

class AgentType(Enum):
    SBDR = "sbdr"
    ACCOUNT_MANAGER = "account_manager"
    CUSTOMER_SUCCESS = "customer_success"

class MessageType(Enum):
    USER_MESSAGE = "user_message"
    AGENT_RESPONSE = "agent_response"
    AGENT_HANDOFF = "agent_handoff"
    SYSTEM_NOTIFICATION = "system_notification"

# Data Models
@dataclass
class UserProfile:
    session_id: str
    name: str = "Guest"
    email: Optional[str] = None
    budget: Optional[str] = None
    product_interest: Optional[str] = None
    use_case: Optional[str] = None
    timeline: Optional[str] = None
    qualification_status: QualificationStatus = QualificationStatus.NOT_STARTED
    conversation_history: List[Dict] = field(default_factory=list)
    engagement_score: int = 0
    current_agent: Optional[AgentType] = None
    customer_tier: str = "prospect"  # prospect, customer, vip
    lifetime_value: float = 0.0
    last_interaction: Optional[datetime] = None

@dataclass
class Message:
    id: str
    session_id: str
    content: str
    message_type: MessageType
    sender: str  # user, agent_name, or system
    timestamp: datetime
    intent: Optional[Intent] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentResponse:
    content: str
    intent: Intent
    confidence: float
    next_agent: Optional[AgentType] = None
    actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

# Base Agent Class
class BaseAgent(ABC):
    def __init__(self, agent_type: AgentType, knowledge_base: Dict[str, Any], integration_manager=None):
        self.agent_type = agent_type
        self.knowledge_base = knowledge_base
        self.name = f"{agent_type.value}_agent"
        self.integration_manager = integration_manager
        
    @abstractmethod
    async def process_message(self, message: Message, user_profile: UserProfile) -> AgentResponse:
        """Process a message and return a response"""
        pass
    
    @abstractmethod
    def can_handle(self, intent: Intent, user_profile: UserProfile) -> bool:
        """Determine if this agent can handle the given intent and user context"""
        pass
    
    def detect_intent(self, message_content: str) -> Intent:
        """Enhanced intent detection based on the original SBDR logic"""
        content_lower = message_content.lower()
        
        # Greeting patterns
        if re.search(r'\b(hello|hi|hey|good\s+(morning|afternoon|evening)|greetings)\b', content_lower):
            return Intent.GREETING
            
        # Product inquiry patterns
        product_patterns = ["laptop", "computer", "phone", "smartphone", "tablet", "headphones"]
        if any(pattern in content_lower for pattern in product_patterns):
            return Intent.PRODUCT_INQUIRY
            
        # Pricing patterns
        if re.search(r'\b(price|cost|budget|how\s+much|expensive|cheap|affordable)\b', content_lower):
            return Intent.PRICING
            
        # Order status patterns
        if re.search(r'\b(order|tracking|delivery|shipped|status|where\s+is\s+my)\b', content_lower):
            return Intent.ORDER_STATUS
            
        # Account management patterns
        if re.search(r'\b(account|profile|subscription|billing|invoice|payment)\b', content_lower):
            return Intent.ACCOUNT_MANAGEMENT
            
        # Customer success patterns
        if re.search(r'\b(onboarding|training|best\s+practices|optimize|usage|tips)\b', content_lower):
            return Intent.CUSTOMER_SUCCESS
            
        # Support patterns
        if re.search(r'\b(help|support|problem|issue|broken|not\s+working|trouble)\b', content_lower):
            return Intent.SUPPORT
            
        # Handoff request patterns
        if re.search(r'\b(human|agent|representative|person|speak\s+to\s+someone|manager)\b', content_lower):
            return Intent.HANDOFF_REQUEST
            
        return Intent.GENERAL

    def extract_qualification_data(self, message_content: str) -> Dict[str, str]:
        """Extract qualification data from message content"""
        content_lower = message_content.lower()
        extracted_data = {}
        
        # Extract budget information
        budget_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*)\s*dollars?',
            r'under\s*\$?(\d+(?:,\d{3})*)',
            r'around\s*\$?(\d+(?:,\d{3})*)',
            r'budget.*?\$?(\d+(?:,\d{3})*)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, content_lower)
            if match:
                extracted_data['budget'] = match.group(1).replace(',', '')
                break
        
        # Extract use case
        use_case_patterns = {
            "business": [r'\b(business|work|office|professional|corporate)\b'],
            "gaming": [r'\b(gaming|game|gamer|esports|streaming)\b'],
            "education": [r'\b(school|student|education|study|learning|college)\b'],
            "creative": [r'\b(design|photo|video|creative|art|editing)\b'],
            "personal": [r'\b(personal|home|family|casual|everyday)\b']
        }
        
        for use_case, patterns in use_case_patterns.items():
            if any(re.search(pattern, content_lower) for pattern in patterns):
                extracted_data['use_case'] = use_case
                break
        
        return extracted_data

# SBDR Agent Implementation
class SBDRAgent(BaseAgent):
    def __init__(self, knowledge_base: Dict[str, Any]):
        super().__init__(AgentType.SBDR, knowledge_base)
        
    def can_handle(self, intent: Intent, user_profile: UserProfile) -> bool:
        """SBDR handles initial qualification and sales inquiries"""
        qualifying_intents = [
            Intent.GREETING, Intent.PRODUCT_INQUIRY, Intent.PRICING, 
            Intent.GENERAL, Intent.QUALIFICATION_RESPONSE
        ]
        return intent in qualifying_intents and user_profile.customer_tier == "prospect"
    
    async def process_message(self, message: Message, user_profile: UserProfile) -> AgentResponse:
        """Process message with SBDR lead qualification logic"""
        intent = self.detect_intent(message.content)
        extracted_data = self.extract_qualification_data(message.content)
        
        # Update user profile with extracted data
        self._update_user_profile(user_profile, extracted_data)
        
        # Generate response based on qualification status
        response_content = await self._generate_response(intent, user_profile, message.content)
        
        # Determine if handoff is needed
        next_agent = self._determine_handoff(user_profile, intent)
        
        # Generate qualification questions if needed
        if self._needs_qualification_questions(user_profile, intent):
            questions = self._generate_qualification_questions(user_profile, intent)
            if questions:
                response_content += "\n\n" + "\n".join(questions)
        
        return AgentResponse(
            content=response_content,
            intent=intent,
            confidence=0.8,
            next_agent=next_agent,
            actions=["qualify_lead", "engage_prospect"],
            metadata={
                "qualification_status": user_profile.qualification_status.value,
                "extracted_data": extracted_data,
                "engagement_score": user_profile.engagement_score
            }
        )
    
    def _update_user_profile(self, profile: UserProfile, extracted_data: Dict[str, str]):
        """Update user profile with qualification data"""
        for field in ['budget', 'product_interest', 'use_case', 'timeline']:
            if field in extracted_data:
                setattr(profile, field, extracted_data[field])
                profile.engagement_score += 1
        
        # Update qualification status
        qualification_fields = [profile.budget, profile.product_interest, profile.use_case]
        filled_fields = sum(1 for field in qualification_fields if field is not None)
        
        if filled_fields == 0:
            profile.qualification_status = QualificationStatus.NOT_STARTED
        elif filled_fields < 3:
            profile.qualification_status = QualificationStatus.IN_PROGRESS
        else:
            profile.qualification_status = QualificationStatus.COMPLETED
            
            # Determine if qualified
            try:
                budget_value = int(profile.budget) if profile.budget else 0
                min_budget = self.knowledge_base.get("escalation_criteria", {}).get("qualified_lead", {}).get("budget_minimum", 500)
                
                if budget_value >= min_budget and profile.product_interest and profile.engagement_score >= 2:
                    profile.qualification_status = QualificationStatus.QUALIFIED
                else:
                    profile.qualification_status = QualificationStatus.UNQUALIFIED
            except (ValueError, TypeError):
                profile.qualification_status = QualificationStatus.IN_PROGRESS
    
    async def _generate_response(self, intent: Intent, profile: UserProfile, message: str) -> str:
        """Generate contextual response using OpenAI or fallback to knowledge base"""
        
        # Try to generate AI response if integration manager is available
        if self.integration_manager and hasattr(self.integration_manager, 'openai'):
            try:
                # Create context for the AI
                system_prompt = f"""You are a Sales Business Development Representative (SBDR) agent helping customers find the right products. 
                
Customer Profile:
- Name: {profile.name}
- Customer Tier: {profile.customer_tier}
- Qualification Status: {profile.qualification_status}
- Budget: {profile.budget or 'Not specified'}
- Product Interest: {profile.product_interest or 'Not specified'}
- Use Case: {profile.use_case or 'Not specified'}

Your goal is to qualify leads, understand their needs, and provide helpful product guidance. Be conversational, helpful, and ask qualifying questions when appropriate."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
                
                ai_response = await self.integration_manager.openai.generate_response(
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                
                if ai_response:
                    return ai_response
                    
            except Exception as e:
                logger.warning(f"AI response generation failed: {e}")
        
        # Fallback to knowledge base responses
        responses = self.knowledge_base.get("common_responses", {})
        
        if intent == Intent.GREETING:
            base_responses = responses.get("greeting", ["Hello! How can I help you today?"])
            return random.choice(base_responses)
        elif intent == Intent.PRODUCT_INQUIRY:
            return f"I'd be happy to help you find the right product! Let me ask you a few questions to understand your needs better."
        elif intent == Intent.PRICING:
            return "I can help you find options within your budget. What type of product are you looking for?"
        else:
            # Check knowledge base for specific answers
            kb_response = self._query_knowledge_base(message)
            if kb_response:
                return kb_response
            return "Thank you for your message. I'm here to help you find the perfect product for your needs."
    
    def _query_knowledge_base(self, query: str) -> Optional[str]:
        """Query knowledge base for relevant information"""
        query_lower = query.lower()
        policies = self.knowledge_base.get("policies", {})
        
        policy_keywords = {
            "shipping": ["ship", "delivery", "arrive"],
            "return": ["return", "refund", "exchange"],
            "warranty": ["warranty", "guarantee", "protection"]
        }
        
        for policy_key, keywords in policy_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                policy_name = f"{policy_key}_policy"
                if policy_name in policies:
                    return policies[policy_name]
        
        return None
    
    def _determine_handoff(self, profile: UserProfile, intent: Intent) -> Optional[AgentType]:
        """Determine if conversation should be handed off"""
        if intent == Intent.HANDOFF_REQUEST:
            return AgentType.ACCOUNT_MANAGER
        
        if profile.qualification_status == QualificationStatus.QUALIFIED:
            return AgentType.ACCOUNT_MANAGER
        
        if profile.customer_tier != "prospect":
            if intent == Intent.ACCOUNT_MANAGEMENT:
                return AgentType.ACCOUNT_MANAGER
            elif intent == Intent.CUSTOMER_SUCCESS:
                return AgentType.CUSTOMER_SUCCESS
        
        return None
    
    def _needs_qualification_questions(self, profile: UserProfile, intent: Intent) -> bool:
        """Check if qualification questions are needed"""
        return (profile.qualification_status in [QualificationStatus.NOT_STARTED, QualificationStatus.IN_PROGRESS] 
                and intent in [Intent.GREETING, Intent.PRODUCT_INQUIRY, Intent.PRICING, Intent.GENERAL])
    
    def _generate_qualification_questions(self, profile: UserProfile, intent: Intent) -> List[str]:
        """Generate contextual qualification questions"""
        questions = []
        question_bank = self.knowledge_base.get("qualification_questions", {})
        
        if not profile.product_interest:
            questions.append(random.choice(question_bank.get("product_questions", 
                ["What type of product are you most interested in?"])))
        
        if not profile.budget:
            questions.append(random.choice(question_bank.get("budget_questions", 
                ["What's your approximate budget for this purchase?"])))
        
        if not profile.use_case and profile.product_interest:
            questions.append(f"What will you primarily use the {profile.product_interest} for?")
        
        return questions[:2]  # Limit to 2 questions

# Account Manager Agent
class AccountManagerAgent(BaseAgent):
    def __init__(self, knowledge_base: Dict[str, Any]):
        super().__init__(AgentType.ACCOUNT_MANAGER, knowledge_base)
    
    def can_handle(self, intent: Intent, user_profile: UserProfile) -> bool:
        """Account Manager handles qualified leads and existing customers"""
        account_intents = [
            Intent.ACCOUNT_MANAGEMENT, Intent.ORDER_STATUS, Intent.HANDOFF_REQUEST,
            Intent.PRODUCT_INQUIRY, Intent.PRICING
        ]
        return (intent in account_intents and 
                (user_profile.qualification_status == QualificationStatus.QUALIFIED or 
                 user_profile.customer_tier in ["customer", "vip"]))
    
    async def process_message(self, message: Message, user_profile: UserProfile) -> AgentResponse:
        """Process message with account management focus"""
        intent = self.detect_intent(message.content)
        
        response_content = await self._generate_account_response(intent, user_profile, message.content)
        
        # Update customer interaction tracking
        user_profile.last_interaction = datetime.now()
        user_profile.current_agent = AgentType.ACCOUNT_MANAGER
        
        # Determine next actions
        actions = self._determine_account_actions(intent, user_profile)
        
        return AgentResponse(
            content=response_content,
            intent=intent,
            confidence=0.9,
            actions=actions,
            metadata={
                "customer_tier": user_profile.customer_tier,
                "lifetime_value": user_profile.lifetime_value,
                "interaction_type": "account_management"
            }
        )
    
    async def _generate_account_response(self, intent: Intent, profile: UserProfile, message: str) -> str:
        """Generate account management response"""
        if intent == Intent.ORDER_STATUS:
            return f"Hello {profile.name}! I'd be happy to help you check on your order status. Let me pull up your account details."
        elif intent == Intent.ACCOUNT_MANAGEMENT:
            return f"Hi {profile.name}! I'm here to help with your account. What can I assist you with today?"
        elif intent == Intent.PRODUCT_INQUIRY:
            if profile.customer_tier == "vip":
                return f"As one of our valued VIP customers, I'd love to show you our latest premium offerings that might interest you."
            else:
                return f"I'd be happy to help you explore our product catalog. Based on your previous interests in {profile.product_interest or 'our products'}, I have some great recommendations."
        elif intent == Intent.HANDOFF_REQUEST:
            return "I'm a senior account manager and I'm here to provide you with personalized service. How can I help you today?"
        else:
            return f"Thank you for reaching out, {profile.name}. I'm here to ensure you have the best possible experience with us."
    
    def _determine_account_actions(self, intent: Intent, profile: UserProfile) -> List[str]:
        """Determine account management actions"""
        actions = ["update_customer_record"]
        
        if intent == Intent.ORDER_STATUS:
            actions.append("check_order_status")
        elif intent == Intent.PRODUCT_INQUIRY:
            actions.extend(["generate_recommendations", "check_inventory"])
        elif intent == Intent.ACCOUNT_MANAGEMENT:
            actions.append("review_account_health")
        
        if profile.customer_tier == "vip":
            actions.append("apply_vip_benefits")
        
        return actions

# Customer Success Agent
class CustomerSuccessAgent(BaseAgent):
    def __init__(self, knowledge_base: Dict[str, Any]):
        super().__init__(AgentType.CUSTOMER_SUCCESS, knowledge_base)
    
    def can_handle(self, intent: Intent, user_profile: UserProfile) -> bool:
        """Customer Success handles existing customers for onboarding and optimization"""
        success_intents = [Intent.CUSTOMER_SUCCESS, Intent.SUPPORT, Intent.GENERAL]
        return (intent in success_intents and 
                user_profile.customer_tier in ["customer", "vip"])
    
    async def process_message(self, message: Message, user_profile: UserProfile) -> AgentResponse:
        """Process message with customer success focus"""
        intent = self.detect_intent(message.content)
        
        response_content = await self._generate_success_response(intent, user_profile, message.content)
        
        # Update customer success tracking
        user_profile.current_agent = AgentType.CUSTOMER_SUCCESS
        user_profile.last_interaction = datetime.now()
        
        actions = self._determine_success_actions(intent, user_profile)
        
        return AgentResponse(
            content=response_content,
            intent=intent,
            confidence=0.85,
            actions=actions,
            metadata={
                "interaction_type": "customer_success",
                "customer_health_score": self._calculate_health_score(user_profile)
            }
        )
    
    async def _generate_success_response(self, intent: Intent, profile: UserProfile, message: str) -> str:
        """Generate customer success response"""
        if intent == Intent.CUSTOMER_SUCCESS:
            return f"Hi {profile.name}! I'm here to help you get the most value from your purchase. What would you like to learn about today?"
        elif intent == Intent.SUPPORT:
            return f"I'd be happy to help you resolve any issues, {profile.name}. Can you tell me more about what you're experiencing?"
        else:
            return f"Hello {profile.name}! As your customer success representative, I'm here to ensure you're maximizing the value of your investment with us."
    
    def _determine_success_actions(self, intent: Intent, profile: UserProfile) -> List[str]:
        """Determine customer success actions"""
        actions = ["track_customer_health"]
        
        if intent == Intent.CUSTOMER_SUCCESS:
            actions.extend(["provide_best_practices", "schedule_check_in"])
        elif intent == Intent.SUPPORT:
            actions.extend(["troubleshoot_issue", "escalate_if_needed"])
        
        # Proactive actions based on customer health
        health_score = self._calculate_health_score(profile)
        if health_score < 0.5:
            actions.append("initiate_retention_workflow")
        
        return actions
    
    def _calculate_health_score(self, profile: UserProfile) -> float:
        """Calculate customer health score"""
        score = 0.5  # Base score
        
        if profile.last_interaction:
            days_since = (datetime.now() - profile.last_interaction).days
            if days_since < 30:
                score += 0.3
            elif days_since < 60:
                score += 0.1
        
        if profile.engagement_score > 5:
            score += 0.2
        
        return min(1.0, score)

# Agent Orchestrator
class AgentOrchestrator:
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.user_profiles: Dict[str, UserProfile] = {}
        self.conversation_history: Dict[str, List[Message]] = {}
        
        # Initialize agents
        self.agents = {
            AgentType.SBDR: SBDRAgent(self.knowledge_base),
            AgentType.ACCOUNT_MANAGER: AccountManagerAgent(self.knowledge_base),
            AgentType.CUSTOMER_SUCCESS: CustomerSuccessAgent(self.knowledge_base)
        }
        
        # Integration handlers
        self.integrations = {}
        
    def set_integration_manager(self, integration_manager):
        """Set integration manager for all agents"""
        for agent in self.agents.values():
            agent.integration_manager = integration_manager
    
    def _load_knowledge_base(self, path: str) -> Dict[str, Any]:
        """Load knowledge base from JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Knowledge base file {path} not found. Using minimal fallback.")
            return self._get_fallback_knowledge_base()
    
    def _get_fallback_knowledge_base(self) -> Dict[str, Any]:
        """Provide fallback knowledge base"""
        return {
            "policies": {
                "shipping_policy": "Standard shipping information available upon request.",
                "return_policy": "Return policy information available upon request."
            },
            "qualification_questions": {
                "budget_questions": ["What's your budget?"],
                "use_case_questions": ["What will you use this for?"],
                "product_questions": ["What type of product interests you?"]
            },
            "common_responses": {
                "greeting": ["Hello! How can I help you today?"]
            },
            "escalation_criteria": {
                "qualified_lead": {"budget_minimum": 500}
            }
        }
    
    def get_or_create_user_profile(self, session_id: str, name: str = "Guest", 
                                 email: Optional[str] = None, customer_tier: str = "prospect") -> UserProfile:
        """Get or create user profile"""
        if session_id not in self.user_profiles:
            self.user_profiles[session_id] = UserProfile(
                session_id=session_id,
                name=name,
                email=email,
                customer_tier=customer_tier
            )
        return self.user_profiles[session_id]
    
    def _select_agent(self, intent: Intent, user_profile: UserProfile) -> BaseAgent:
        """Select the appropriate agent based on intent and user context"""
        # Try agents in priority order
        for agent_type in [AgentType.ACCOUNT_MANAGER, AgentType.CUSTOMER_SUCCESS, AgentType.SBDR]:
            agent = self.agents[agent_type]
            if agent.can_handle(intent, user_profile):
                logger.info(f"Selected {agent_type.value} for intent {intent.value}")
                return agent
        
        # Default to SBDR agent
        return self.agents[AgentType.SBDR]
    
    async def process_message(self, session_id: str, message_content: str, 
                            user_name: str = "Guest", user_email: Optional[str] = None,
                            customer_tier: str = "prospect") -> Dict[str, Any]:
        """Process a message through the multi-agent system"""
        # Get or create user profile
        user_profile = self.get_or_create_user_profile(session_id, user_name, user_email, customer_tier)
        
        # Create message object
        message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            content=message_content,
            message_type=MessageType.USER_MESSAGE,
            sender="user",
            timestamp=datetime.now()
        )
        
        # Detect intent
        intent = Intent.GENERAL
        for agent in self.agents.values():
            detected_intent = agent.detect_intent(message_content)
            if detected_intent != Intent.GENERAL:
                intent = detected_intent
                break
        
        message.intent = intent
        
        # Select appropriate agent
        selected_agent = self._select_agent(intent, user_profile)
        user_profile.current_agent = selected_agent.agent_type
        
        # Process message
        response = await selected_agent.process_message(message, user_profile)
        
        # Handle agent handoff if needed
        if response.next_agent and response.next_agent != selected_agent.agent_type:
            handoff_agent = self.agents[response.next_agent]
            user_profile.current_agent = response.next_agent
            response = await handoff_agent.process_message(message, user_profile)
            response.metadata["handoff_occurred"] = True
            response.metadata["previous_agent"] = selected_agent.agent_type.value
        
        # Store conversation history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].extend([
            message,
            Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                content=response.content,
                message_type=MessageType.AGENT_RESPONSE,
                sender=selected_agent.name,
                timestamp=datetime.now(),
                intent=response.intent
            )
        ])
        
        # Update user profile conversation history
        user_profile.conversation_history.append({
            "message": message_content,
            "response": response.content,
            "intent": response.intent.value,
            "agent": selected_agent.agent_type.value,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response.content,
            "intent": response.intent.value,
            "agent": selected_agent.agent_type.value,
            "confidence": response.confidence,
            "actions": response.actions,
            "user_profile": {
                "qualification_status": user_profile.qualification_status.value,
                "customer_tier": user_profile.customer_tier,
                "engagement_score": user_profile.engagement_score,
                "current_agent": user_profile.current_agent.value if user_profile.current_agent else None
            },
            "metadata": response.metadata
        }
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary for a session"""
        if session_id not in self.user_profiles:
            return {}
        
        profile = self.user_profiles[session_id]
        history = self.conversation_history.get(session_id, [])
        
        return {
            "session_id": session_id,
            "user_profile": asdict(profile),
            "conversation_length": len(history),
            "agents_involved": list(set([msg.sender for msg in history if msg.message_type == MessageType.AGENT_RESPONSE])),
            "intents_detected": list(set([msg.intent.value for msg in history if msg.intent])),
            "last_interaction": profile.last_interaction.isoformat() if profile.last_interaction else None
        }

# Integration Layer (placeholder for Crisp, Shopify, etc.)
class IntegrationManager:
    def __init__(self):
        self.crisp_config = {}
        self.shopify_config = {}
    
    async def send_to_crisp(self, session_id: str, message: str) -> bool:
        """Send message to Crisp (placeholder)"""
        logger.info(f"Sending to Crisp [{session_id}]: {message}")
        return True
    
    async def get_shopify_products(self, query: str) -> List[Dict]:
        """Get products from Shopify (placeholder)"""
        logger.info(f"Querying Shopify products: {query}")
        return []
    
    async def get_customer_orders(self, customer_email: str) -> List[Dict]:
        """Get customer orders from Shopify (placeholder)"""
        logger.info(f"Getting orders for customer: {customer_email}")
        return []

# Main execution example
async def main():
    """Example usage of the multi-agent system"""
    orchestrator = AgentOrchestrator()
    
    # Simulate a conversation flow
    test_scenarios = [
        {
            "session_id": "session_1",
            "customer_tier": "prospect",
            "messages": [
                "Hi, I'm looking for a laptop for work",
                "My budget is around $1200",
                "I need it for business presentations and some design work",
                "Can I speak to someone about specific models?"
            ]
        },
        {
            "session_id": "session_2",
            "customer_tier": "customer",
            "messages": [
                "Hi, I need to check on my recent order",
                "Also, I'd like to know about warranty options",
                "Can you help me optimize my setup?"
            ]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario['session_id']} ({scenario['customer_tier']})")
        print(f"{'='*60}")
        
        for i, message in enumerate(scenario['messages']):
            result = await orchestrator.process_message(
                session_id=scenario['session_id'],
                message_content=message,
                customer_tier=scenario['customer_tier']
            )
            
            print(f"\nMessage {i+1}: {message}")
            print(f"Agent: {result['agent']}")
            print(f"Response: {result['response']}")
            print(f"Intent: {result['intent']}")
            print(f"Actions: {result['actions']}")
            print(f"Status: {result['user_profile']['qualification_status']}")
            print("-" * 40)
        
        # Show conversation summary
        summary = orchestrator.get_conversation_summary(scenario['session_id'])
        print(f"\nConversation Summary:")
        print(f"- Length: {summary['conversation_length']} messages")
        print(f"- Agents: {summary['agents_involved']}")
        print(f"- Intents: {summary['intents_detected']}")

if __name__ == "__main__":
    asyncio.run(main())