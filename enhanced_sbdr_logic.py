"""
Enhanced SBDR Agent Logic with JSON Knowledge Base Integration
This module provides an improved version of the SBDR agent that loads
configuration and responses from a JSON knowledge base file.
"""

import json
import re
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

class Intent(Enum):
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    PRICING = "pricing"
    ORDER_STATUS = "order_status"
    SHIPPING = "shipping"
    SUPPORT = "support"
    HANDOFF_REQUEST = "handoff_request"
    QUALIFICATION_RESPONSE = "qualification_response"
    GENERAL = "general"

class QualificationStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    QUALIFIED = "qualified"
    UNQUALIFIED = "unqualified"

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
    conversation_history: List[Dict] = None
    engagement_score: int = 0
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class EnhancedSBDRAgent:
    def __init__(self, knowledge_base_path: str = "knowledge_base.json"):
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self.user_profiles: Dict[str, UserProfile] = {}
        
    def _load_knowledge_base(self, path: str) -> Dict[str, Any]:
        """Load knowledge base from JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Knowledge base file {path} not found. Using minimal fallback.")
            return self._get_fallback_knowledge_base()
    
    def _get_fallback_knowledge_base(self) -> Dict[str, Any]:
        """Provide a minimal fallback knowledge base."""
        return {
            "policies": {
                "shipping_policy": "Standard shipping information available upon request.",
                "return_policy": "Return policy information available upon request.",
                "warranty": "Warranty information available upon request."
            },
            "product_categories": {},
            "qualification_questions": {
                "budget_questions": ["What's your budget?"],
                "use_case_questions": ["What will you use this for?"]
            },
            "common_responses": {
                "greeting": ["Hello! How can I help you today?"]
            }
        }
    
    def detect_intent(self, message: str) -> Intent:
        """Enhanced intent detection with better pattern matching."""
        message_lower = message.lower()
        
        # Greeting patterns
        greeting_patterns = [
            r'\b(hello|hi|hey|good\s+(morning|afternoon|evening)|greetings)\b',
            r'\b(howdy|what\'s\s+up|sup)\b'
        ]
        if any(re.search(pattern, message_lower) for pattern in greeting_patterns):
            return Intent.GREETING
            
        # Product inquiry patterns
        product_categories = list(self.knowledge_base.get("product_categories", {}).keys())
        product_patterns = product_categories + [
            "laptop", "computer", "phone", "smartphone", "tablet", "headphones", 
            "earbuds", "smartwatch", "watch", "monitor", "keyboard", "mouse"
        ]
        if any(pattern in message_lower for pattern in product_patterns):
            return Intent.PRODUCT_INQUIRY
            
        # Pricing patterns
        pricing_patterns = [
            r'\b(price|cost|budget|how\s+much|expensive|cheap|affordable)\b',
            r'\$\d+', r'\d+\s*dollars?'
        ]
        if any(re.search(pattern, message_lower) for pattern in pricing_patterns):
            return Intent.PRICING
            
        # Order status patterns
        order_patterns = [
            r'\b(order|tracking|delivery|shipped|status|where\s+is\s+my)\b'
        ]
        if any(re.search(pattern, message_lower) for pattern in order_patterns):
            return Intent.ORDER_STATUS
            
        # Shipping patterns
        shipping_patterns = [
            r'\b(shipping|delivery|when\s+will|how\s+long|arrive|fast)\b'
        ]
        if any(re.search(pattern, message_lower) for pattern in shipping_patterns):
            return Intent.SHIPPING
            
        # Support patterns
        support_patterns = [
            r'\b(help|support|problem|issue|broken|not\s+working|trouble)\b'
        ]
        if any(re.search(pattern, message_lower) for pattern in support_patterns):
            return Intent.SUPPORT
            
        # Handoff request patterns
        handoff_patterns = [
            r'\b(human|agent|representative|person|speak\s+to\s+someone|manager)\b'
        ]
        if any(re.search(pattern, message_lower) for pattern in handoff_patterns):
            return Intent.HANDOFF_REQUEST
            
        return Intent.GENERAL
    
    def extract_qualification_data(self, message: str) -> Dict[str, Optional[str]]:
        """Enhanced qualification data extraction."""
        message_lower = message.lower()
        extracted_data = {}
        
        # Extract budget information with more patterns
        budget_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*)\s*dollars?',
            r'under\s*\$?(\d+(?:,\d{3})*)',
            r'around\s*\$?(\d+(?:,\d{3})*)',
            r'about\s*\$?(\d+(?:,\d{3})*)',
            r'budget.*?\$?(\d+(?:,\d{3})*)',
            r'(\d+(?:,\d{3})*)\s*buck',
            r'up\s+to\s*\$?(\d+(?:,\d{3})*)'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, message_lower)
            if match:
                extracted_data['budget'] = match.group(1).replace(',', '')
                break
                
        # Extract product interest from knowledge base categories
        product_categories = self.knowledge_base.get("product_categories", {})
        for category, info in product_categories.items():
            brands = info.get("popular_brands", [])
            if category in message_lower:
                extracted_data['product_interest'] = category
                break
            # Check for brand mentions
            for brand in brands:
                if brand.lower() in message_lower:
                    extracted_data['product_interest'] = category
                    break
                    
        # Extract use case with expanded patterns
        use_case_patterns = {
            "business": [r'\b(business|work|office|professional|corporate)\b'],
            "gaming": [r'\b(gaming|game|gamer|esports|streaming)\b'],
            "education": [r'\b(school|student|education|study|learning|college)\b'],
            "creative": [r'\b(design|photo|video|creative|art|editing)\b'],
            "personal": [r'\b(personal|home|family|casual|everyday)\b'],
            "fitness": [r'\b(fitness|workout|exercise|health|running)\b']
        }
        
        for use_case, patterns in use_case_patterns.items():
            if any(re.search(pattern, message_lower) for pattern in patterns):
                extracted_data['use_case'] = use_case
                break
                
        # Extract timeline information
        timeline_patterns = {
            "immediate": [r'\b(now|today|asap|immediately|urgent)\b'],
            "this_week": [r'\b(this\s+week|within\s+a\s+week|soon)\b'],
            "this_month": [r'\b(this\s+month|within\s+a\s+month)\b'],
            "researching": [r'\b(research|looking|browsing|comparing|just\s+checking)\b']
        }
        
        for timeline, patterns in timeline_patterns.items():
            if any(re.search(pattern, message_lower) for pattern in patterns):
                extracted_data['timeline'] = timeline
                break
                
        return extracted_data
    
    def get_or_create_user_profile(self, session_id: str, name: str = "Guest", 
                                 email: Optional[str] = None) -> UserProfile:
        """Get existing user profile or create a new one."""
        if session_id not in self.user_profiles:
            self.user_profiles[session_id] = UserProfile(
                session_id=session_id,
                name=name,
                email=email
            )
        return self.user_profiles[session_id]
    
    def update_user_profile(self, session_id: str, extracted_data: Dict[str, str]) -> None:
        """Update user profile with extracted qualification data."""
        if session_id in self.user_profiles:
            profile = self.user_profiles[session_id]
            
            # Update profile fields
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
                
                # Determine if qualified based on criteria
                escalation_criteria = self.knowledge_base.get("escalation_criteria", {})
                qualified_criteria = escalation_criteria.get("qualified_lead", {})
                
                try:
                    budget_value = int(profile.budget) if profile.budget else 0
                    min_budget = qualified_criteria.get("budget_minimum", 100)
                    
                    if (budget_value >= min_budget and 
                        profile.product_interest and 
                        profile.engagement_score >= 2):
                        profile.qualification_status = QualificationStatus.QUALIFIED
                    else:
                        profile.qualification_status = QualificationStatus.UNQUALIFIED
                except (ValueError, TypeError):
                    profile.qualification_status = QualificationStatus.IN_PROGRESS
    
    def generate_qualification_questions(self, profile: UserProfile, intent: Intent) -> List[str]:
        """Generate contextual qualification questions."""
        questions = []
        question_bank = self.knowledge_base.get("qualification_questions", {})
        
        if not profile.product_interest:
            if intent == Intent.PRODUCT_INQUIRY:
                questions.append("What specific type of product are you looking for?")
            else:
                questions.append(random.choice(
                    question_bank.get("product_questions", 
                    ["What type of product interests you most?"])
                ))
                
        if not profile.budget:
            questions.append(random.choice(
                question_bank.get("budget_questions", 
                ["What's your approximate budget?"])
            ))
            
        if not profile.use_case:
            if profile.product_interest:
                questions.append(f"What will you primarily use the {profile.product_interest} for?")
            else:
                questions.append(random.choice(
                    question_bank.get("use_case_questions", 
                    ["What will you primarily use this for?"])
                ))
                
        if not profile.timeline and len(questions) < 2:
            questions.append(random.choice(
                question_bank.get("timeline_questions", 
                ["When are you looking to make this purchase?"])
            ))
                
        return questions[:2]  # Limit to 2 questions to avoid overwhelming
    
    def query_knowledge_base(self, query: str) -> Optional[str]:
        """Enhanced knowledge base querying with better matching."""
        query_lower = query.lower()
        policies = self.knowledge_base.get("policies", {})
        
        # Direct policy matching
        policy_keywords = {
            "shipping": ["ship", "delivery", "arrive", "fast"],
            "return": ["return", "refund", "exchange"],
            "warranty": ["warranty", "guarantee", "protection"],
            "payment": ["payment", "pay", "credit", "paypal"],
            "price_matching": ["price match", "match price", "competitor"]
        }
        
        for policy_key, keywords in policy_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                policy_name = f"{policy_key}_policy" if policy_key != "price_matching" else policy_key
                if policy_name in policies:
                    return policies[policy_name]
        
        # Product category information
        product_categories = self.knowledge_base.get("product_categories", {})
        for category, info in product_categories.items():
            if category in query_lower:
                description = info.get("description", "")
                price_range = info.get("price_range", "")
                brands = ", ".join(info.get("popular_brands", [])[:3])
                
                return f"{description} Price range: {price_range}. Popular brands include: {brands}."
        
        return None
    
    def should_handoff(self, profile: UserProfile, intent: Intent) -> bool:
        """Determine if conversation should be handed off to human agent."""
        escalation_criteria = self.knowledge_base.get("escalation_criteria", {})
        
        # Immediate handoff triggers
        immediate_triggers = escalation_criteria.get("immediate_handoff", {})
        if intent == Intent.HANDOFF_REQUEST:
            return True
            
        # Qualified lead handoff
        if profile.qualification_status == QualificationStatus.QUALIFIED:
            return True
            
        # Complex inquiry handoff
        if (len(profile.conversation_history) > 5 and 
            profile.qualification_status == QualificationStatus.COMPLETED):
            return True
            
        # High engagement but unqualified
        if (profile.engagement_score > 3 and 
            profile.qualification_status == QualificationStatus.UNQUALIFIED):
            return True
            
        return False
    
    def generate_response(self, session_id: str, message: str, ai_response: str) -> Dict[str, Any]:
        """Generate comprehensive response with all context."""
        intent = self.detect_intent(message)
        extracted_data = self.extract_qualification_data(message)
        
        # Get or create user profile
        profile = self.get_or_create_user_profile(session_id)
        
        # Update profile with extracted data
        self.update_user_profile(session_id, extracted_data)
        
        # Add message to conversation history
        profile.conversation_history.append({
            "message": message,
            "intent": intent.value,
            "extracted_data": extracted_data,
            "timestamp": "now"
        })
        
        # Check knowledge base first
        kb_answer = self.query_knowledge_base(message)
        if kb_answer:
            final_response = kb_answer
        else:
            # Use AI response with potential enhancements
            common_responses = self.knowledge_base.get("common_responses", {})
            if intent.value in common_responses:
                # Optionally enhance AI response with template
                final_response = ai_response
            else:
                final_response = ai_response
        
        # Add qualification questions if needed
        needs_qualification = (
            profile.qualification_status in [QualificationStatus.NOT_STARTED, QualificationStatus.IN_PROGRESS] and
            intent in [Intent.PRODUCT_INQUIRY, Intent.PRICING, Intent.GENERAL, Intent.GREETING]
        )
        
        qualification_questions = []
        if needs_qualification:
            qualification_questions = self.generate_qualification_questions(profile, intent)
            if qualification_questions:
                final_response += "\n\n" + "\n".join(qualification_questions)
        
        # Determine handoff need
        needs_handoff = self.should_handoff(profile, intent)
        
        if needs_handoff:
            handoff_messages = self.knowledge_base.get("common_responses", {}).get("handoff_triggers", [
                "Let me connect you with one of our specialists who can provide more detailed assistance."
            ])
            final_response += "\n\n" + random.choice(handoff_messages)
        
        return {
            "final_response": final_response,
            "intent": intent.value,
            "qualification_status": profile.qualification_status.value,
            "needs_qualification": needs_qualification,
            "needs_handoff": needs_handoff,
            "engagement_score": profile.engagement_score,
            "user_profile": {
                "budget": profile.budget,
                "product_interest": profile.product_interest,
                "use_case": profile.use_case,
                "timeline": profile.timeline
            },
            "extracted_data": extracted_data
        }
    
    def get_user_profile_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the user profile for handoff purposes."""
        if session_id in self.user_profiles:
            profile = self.user_profiles[session_id]
            return {
                "session_id": session_id,
                "qualification_status": profile.qualification_status.value,
                "user_data": asdict(profile),
                "conversation_summary": {
                    "total_messages": len(profile.conversation_history),
                    "engagement_score": profile.engagement_score,
                    "key_intents": list(set([msg.get("intent") for msg in profile.conversation_history]))
                }
            }
        return {}

# Example usage and testing
if __name__ == "__main__":
    agent = EnhancedSBDRAgent("knowledge_base.json")
    
    # Test scenarios
    test_conversations = [
        {
            "session_id": "session_1",
            "messages": [
                "Hi, I'm looking for a laptop for work",
                "My budget is around $1200",
                "I need it for business presentations and some light photo editing",
                "When can I get it delivered?"
            ]
        },
        {
            "session_id": "session_2", 
            "messages": [
                "What's your return policy?",
                "I'm interested in smartphones",
                "Around $800 budget"
            ]
        }
    ]
    
    for conversation in test_conversations:
        print(f"\n{'='*60}")
        print(f"CONVERSATION: {conversation['session_id']}")
        print(f"{'='*60}")
        
        for i, message in enumerate(conversation['messages']):
            ai_response = f"Thank you for your message about: '{message}'"
            result = agent.generate_response(conversation['session_id'], message, ai_response)
            
            print(f"\nMessage {i+1}: {message}")
            print(f"Response: {result['final_response']}")
            print(f"Intent: {result['intent']}")
            print(f"Status: {result['qualification_status']}")
            print(f"Handoff: {result['needs_handoff']}")
            print(f"Engagement: {result['engagement_score']}")
            print("-" * 40)
        
        # Show final profile summary
        summary = agent.get_user_profile_summary(conversation['session_id'])
        print(f"\nFinal Profile Summary:")
        print(f"Qualification: {summary['qualification_status']}")
        print(f"User Data: {summary['user_data']['budget']}, {summary['user_data']['product_interest']}, {summary['user_data']['use_case']}")

