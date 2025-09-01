"""
SBDR Agent Logic Module
Handles lead qualification, intent detection, and response generation
for the Sales Business Development Representative conversational agent.
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

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
    qualification_status: QualificationStatus = QualificationStatus.NOT_STARTED
    conversation_history: List[Dict] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

@dataclass
class QualificationCriteria:
    min_budget: int = 100
    target_products: List[str] = None
    priority_use_cases: List[str] = None
    
    def __post_init__(self):
        if self.target_products is None:
            self.target_products = ["laptop", "smartphone", "tablet", "headphones", "smartwatch"]
        if self.priority_use_cases is None:
            self.priority_use_cases = ["business", "gaming", "professional", "work", "education"]

class SBDRAgent:
    def __init__(self):
        self.qualification_criteria = QualificationCriteria()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> Dict[str, str]:
        """Load the knowledge base with common questions and answers."""
        return {
            "shipping_policy": "We offer free shipping on orders over $50. Standard shipping takes 3-5 business days, and express shipping takes 1-2 business days.",
            "return_policy": "We accept returns within 30 days of purchase. Items must be in original condition with all packaging and accessories.",
            "warranty": "All our products come with manufacturer warranty. Extended warranty options are available at checkout.",
            "payment_methods": "We accept all major credit cards, PayPal, Apple Pay, and Google Pay.",
            "store_hours": "Our customer service is available Monday-Friday 9AM-6PM EST. Live chat is available 24/7.",
            "price_matching": "We offer price matching on identical products from authorized retailers. Contact us with the competitor's price for verification.",
            "bulk_orders": "For bulk orders (10+ items), please contact our sales team for special pricing and dedicated support.",
            "technical_support": "Technical support is available for all purchased products. Contact us via chat, email, or phone for assistance."
        }
    
    def detect_intent(self, message: str) -> Intent:
        """Detect the intent of the user's message using keyword matching."""
        message_lower = message.lower()
        
        # Greeting patterns
        greeting_patterns = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
        if any(pattern in message_lower for pattern in greeting_patterns):
            return Intent.GREETING
            
        # Product inquiry patterns
        product_patterns = ["laptop", "phone", "smartphone", "tablet", "headphones", "smartwatch", 
                          "computer", "monitor", "keyboard", "mouse", "speaker", "camera"]
        if any(pattern in message_lower for pattern in product_patterns):
            return Intent.PRODUCT_INQUIRY
            
        # Pricing patterns
        pricing_patterns = ["price", "cost", "budget", "how much", "expensive", "cheap", "affordable"]
        if any(pattern in message_lower for pattern in pricing_patterns):
            return Intent.PRICING
            
        # Order status patterns
        order_patterns = ["order", "tracking", "delivery", "shipped", "status"]
        if any(pattern in message_lower for pattern in order_patterns):
            return Intent.ORDER_STATUS
            
        # Shipping patterns
        shipping_patterns = ["shipping", "delivery", "when will", "how long", "arrive"]
        if any(pattern in message_lower for pattern in shipping_patterns):
            return Intent.SHIPPING
            
        # Support patterns
        support_patterns = ["help", "support", "problem", "issue", "broken", "not working"]
        if any(pattern in message_lower for pattern in support_patterns):
            return Intent.SUPPORT
            
        # Handoff request patterns
        handoff_patterns = ["human", "agent", "representative", "person", "speak to someone"]
        if any(pattern in message_lower for pattern in handoff_patterns):
            return Intent.HANDOFF_REQUEST
            
        return Intent.GENERAL
    
    def extract_qualification_data(self, message: str) -> Dict[str, Optional[str]]:
        """Extract qualification data from user messages."""
        message_lower = message.lower()
        extracted_data = {}
        
        # Extract budget information
        budget_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $1,000.00 format
            r'(\d+(?:,\d{3})*)\s*dollars?',      # 1000 dollars format
            r'under\s*\$?(\d+(?:,\d{3})*)',      # under $500 format
            r'around\s*\$?(\d+(?:,\d{3})*)',     # around $300 format
            r'budget.*?\$?(\d+(?:,\d{3})*)',     # budget is $400 format
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, message_lower)
            if match:
                extracted_data['budget'] = match.group(1)
                break
                
        # Extract product interest
        product_keywords = {
            "laptop": ["laptop", "notebook", "computer"],
            "smartphone": ["phone", "smartphone", "mobile"],
            "tablet": ["tablet", "ipad"],
            "headphones": ["headphones", "earbuds", "earphones"],
            "smartwatch": ["watch", "smartwatch", "wearable"],
            "monitor": ["monitor", "display", "screen"],
            "gaming": ["gaming", "game", "gamer"]
        }
        
        for product, keywords in product_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted_data['product_interest'] = product
                break
                
        # Extract use case
        use_case_keywords = {
            "business": ["business", "work", "office", "professional"],
            "gaming": ["gaming", "game", "gamer", "esports"],
            "education": ["school", "student", "education", "study"],
            "creative": ["design", "photo", "video", "creative", "art"],
            "personal": ["personal", "home", "family", "casual"]
        }
        
        for use_case, keywords in use_case_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                extracted_data['use_case'] = use_case
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
            
            if 'budget' in extracted_data:
                profile.budget = extracted_data['budget']
            if 'product_interest' in extracted_data:
                profile.product_interest = extracted_data['product_interest']
            if 'use_case' in extracted_data:
                profile.use_case = extracted_data['use_case']
                
            # Update qualification status
            if profile.budget and profile.product_interest and profile.use_case:
                profile.qualification_status = QualificationStatus.COMPLETED
                
                # Determine if qualified based on criteria
                try:
                    budget_value = int(profile.budget.replace(',', ''))
                    if (budget_value >= self.qualification_criteria.min_budget and
                        profile.product_interest in self.qualification_criteria.target_products):
                        profile.qualification_status = QualificationStatus.QUALIFIED
                    else:
                        profile.qualification_status = QualificationStatus.UNQUALIFIED
                except (ValueError, AttributeError):
                    profile.qualification_status = QualificationStatus.IN_PROGRESS
            elif any([profile.budget, profile.product_interest, profile.use_case]):
                profile.qualification_status = QualificationStatus.IN_PROGRESS
    
    def generate_qualification_questions(self, profile: UserProfile, intent: Intent) -> List[str]:
        """Generate appropriate qualification questions based on user profile and intent."""
        questions = []
        
        if not profile.product_interest:
            if intent == Intent.PRODUCT_INQUIRY:
                questions.append("What type of product are you looking for today?")
            else:
                questions.append("Are you interested in any particular product category? (laptops, smartphones, tablets, etc.)")
                
        if not profile.budget:
            questions.append("What's your approximate budget for this purchase?")
            
        if not profile.use_case:
            if profile.product_interest:
                questions.append(f"What will you primarily use the {profile.product_interest} for?")
            else:
                questions.append("What will you primarily use this product for? (work, gaming, personal use, etc.)")
                
        return questions
    
    def query_knowledge_base(self, query: str) -> Optional[str]:
        """Query the knowledge base for relevant information."""
        query_lower = query.lower()
        
        for key, answer in self.knowledge_base.items():
            if key.replace('_', ' ') in query_lower:
                return answer
                
        # Keyword-based matching
        keyword_mapping = {
            "ship": "shipping_policy",
            "return": "return_policy",
            "warranty": "warranty",
            "payment": "payment_methods",
            "hours": "store_hours",
            "price match": "price_matching",
            "bulk": "bulk_orders",
            "support": "technical_support"
        }
        
        for keyword, key in keyword_mapping.items():
            if keyword in query_lower:
                return self.knowledge_base[key]
                
        return None
    
    def generate_response(self, session_id: str, message: str, ai_response: str) -> Dict[str, any]:
        """Generate the final response including qualification questions if needed."""
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
            "timestamp": "now"  # In real implementation, use actual timestamp
        })
        
        # Check if knowledge base can answer the question
        kb_answer = self.query_knowledge_base(message)
        if kb_answer:
            final_response = kb_answer
        else:
            final_response = ai_response
            
        # Add qualification questions if needed
        needs_qualification = (
            profile.qualification_status in [QualificationStatus.NOT_STARTED, QualificationStatus.IN_PROGRESS] and
            intent in [Intent.PRODUCT_INQUIRY, Intent.PRICING, Intent.GENERAL]
        )
        
        qualification_questions = []
        if needs_qualification:
            qualification_questions = self.generate_qualification_questions(profile, intent)
            if qualification_questions:
                final_response += "\n\n" + "\n".join(qualification_questions)
        
        # Determine if handoff is needed
        needs_handoff = (
            intent == Intent.HANDOFF_REQUEST or
            profile.qualification_status == QualificationStatus.QUALIFIED or
            (profile.qualification_status == QualificationStatus.COMPLETED and 
             len(profile.conversation_history) > 5)
        )
        
        return {
            "final_response": final_response,
            "intent": intent.value,
            "qualification_status": profile.qualification_status.value,
            "needs_qualification": needs_qualification,
            "needs_handoff": needs_handoff,
            "user_profile": {
                "budget": profile.budget,
                "product_interest": profile.product_interest,
                "use_case": profile.use_case
            }
        }

# Example usage and testing
if __name__ == "__main__":
    agent = SBDRAgent()
    
    # Test scenarios
    test_messages = [
        ("session_1", "Hi, I'm looking for a laptop"),
        ("session_1", "My budget is around $1000"),
        ("session_1", "I need it for work and some light gaming"),
        ("session_2", "What's your return policy?"),
        ("session_3", "I want to speak to a human agent")
    ]
    
    for session_id, message in test_messages:
        ai_response = f"Thank you for your message: '{message}'"
        result = agent.generate_response(session_id, message, ai_response)
        print(f"\nSession: {session_id}")
        print(f"Message: {message}")
        print(f"Response: {result['final_response']}")
        print(f"Intent: {result['intent']}")
        print(f"Qualification Status: {result['qualification_status']}")
        print(f"Needs Handoff: {result['needs_handoff']}")
        print("-" * 50)

