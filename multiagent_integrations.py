"""
Multi-Agent SBDR System - Integration Layer
Real integrations with Crisp, Shopify, and external AI services.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Configuration Classes
@dataclass
class CrispConfig:
    identifier: str
    key: str
    website_id: str
    base_url: str = "https://api.crisp.chat/v1"

@dataclass 
class ShopifyConfig:
    shop_domain: str
    access_token: str
    api_version: str = "2023-10"
    
    @property
    def base_url(self) -> str:
        return f"https://{self.shop_domain}.myshopify.com/admin/api/{self.api_version}"

@dataclass
class OpenAIConfig:
    api_key: str
    model: str = "gpt-3.5-turbo"
    base_url: str = "https://api.openai.com/v1"

# Base Integration Class
class BaseIntegration(ABC):
    def __init__(self, config: Any):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_created = False
    
    async def _ensure_session(self):
        """Ensure session is created"""
        if not self.session and not self._session_created:
            self.session = aiohttp.ClientSession()
            self._session_created = True
    
    async def __aenter__(self):
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            self.session = None
            self._session_created = False
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if the integration is working"""
        pass

# Crisp Integration
class CrispIntegration(BaseIntegration):
    def __init__(self, config: CrispConfig):
        super().__init__(config)
        self.config: CrispConfig = config
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for Crisp API"""
        import base64
        credentials = base64.b64encode(
            f"{self.config.identifier}:{self.config.key}".encode()
        ).decode()
        
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "X-Crisp-Tier": "plugin"
        }
    
    async def test_connection(self) -> bool:
        """Test Crisp API connection"""
        try:
            url = f"{self.config.base_url}/website/{self.config.website_id}"
            async with self.session.get(url, headers=self._get_headers()) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Crisp connection test failed: {e}")
            return False
    
    async def send_message(self, session_id: str, content: str, 
                          message_type: str = "text") -> bool:
        """Send message to Crisp conversation"""
        try:
            url = f"{self.config.base_url}/website/{self.config.website_id}/conversation/{session_id}/message"
            
            payload = {
                "type": message_type,
                "content": content,
                "from": "operator",
                "origin": "chat"
            }
            
            async with self.session.post(
                url, 
                json=payload, 
                headers=self._get_headers()
            ) as response:
                if response.status == 201:
                    logger.info(f"Message sent to Crisp session {session_id}")
                    return True
                else:
                    logger.error(f"Failed to send message: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending Crisp message: {e}")
            return False
    
    async def get_conversation_meta(self, session_id: str) -> Optional[Dict]:
        """Get conversation metadata"""
        try:
            url = f"{self.config.base_url}/website/{self.config.website_id}/conversation/{session_id}/meta"
            
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    return await response.json()
                return None
                
        except Exception as e:
            logger.error(f"Error getting conversation meta: {e}")
            return None
    
    async def update_conversation_state(self, session_id: str, state: str) -> bool:
        """Update conversation state (resolved, unresolved, etc.)"""
        try:
            url = f"{self.config.base_url}/website/{self.config.website_id}/conversation/{session_id}/state"
            
            payload = {"state": state}
            
            async with self.session.patch(
                url, 
                json=payload, 
                headers=self._get_headers()
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error updating conversation state: {e}")
            return False

# Shopify Integration
class ShopifyIntegration(BaseIntegration):
    def __init__(self, config: ShopifyConfig):
        super().__init__(config)
        self.config: ShopifyConfig = config
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for Shopify API"""
        return {
            "X-Shopify-Access-Token": self.config.access_token,
            "Content-Type": "application/json"
        }
    
    async def test_connection(self) -> bool:
        """Test Shopify API connection"""
        try:
            url = f"{self.config.base_url}/shop.json"
            async with self.session.get(url, headers=self._get_headers()) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Shopify connection test failed: {e}")
            return False
    
    async def search_products(self, query: str, limit: int = 10, 
                            product_type: Optional[str] = None) -> List[Dict]:
        """Search for products in Shopify"""
        try:
            url = f"{self.config.base_url}/products.json"
            params = {"limit": limit}
            
            if query:
                params["title"] = query
            if product_type:
                params["product_type"] = product_type
            
            async with self.session.get(
                url, 
                params=params, 
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_products(data.get("products", []))
                else:
                    logger.error(f"Product search failed: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return []
    
    async def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get specific product by ID"""
        try:
            url = f"{self.config.base_url}/products/{product_id}.json"
            
            async with self.session.get(url, headers=self._get_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    products = self._format_products([data.get("product")])
                    return products[0] if products else None
                return None
                
        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return None
    
    async def get_customer_orders(self, customer_email: str) -> List[Dict]:
        """Get orders for a customer"""
        try:
            # First find customer
            customer = await self._find_customer_by_email(customer_email)
            if not customer:
                return []
            
            url = f"{self.config.base_url}/orders.json"
            params = {"customer_id": customer["id"], "status": "any"}
            
            async with self.session.get(
                url, 
                params=params, 
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._format_orders(data.get("orders", []))
                return []
                
        except Exception as e:
            logger.error(f"Error getting customer orders: {e}")
            return []
    
    async def _find_customer_by_email(self, email: str) -> Optional[Dict]:
        """Find customer by email"""
        try:
            url = f"{self.config.base_url}/customers/search.json"
            params = {"query": f"email:{email}"}
            
            async with self.session.get(
                url, 
                params=params, 
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    customers = data.get("customers", [])
                    return customers[0] if customers else None
                return None
                
        except Exception as e:
            logger.error(f"Error finding customer: {e}")
            return None
    
    def _format_products(self, products: List[Dict]) -> List[Dict]:
        """Format products for consistent API response"""
        formatted = []
        
        for product in products:
            if not product:
                continue
                
            variants = product.get("variants", [])
            main_variant = variants[0] if variants else {}
            
            formatted_product = {
                "id": product.get("id"),
                "title": product.get("title", ""),
                "description": product.get("body_html", ""),
                "product_type": product.get("product_type", ""),
                "vendor": product.get("vendor", ""),
                "price": main_variant.get("price", "0"),
                "compare_at_price": main_variant.get("compare_at_price"),
                "inventory_quantity": main_variant.get("inventory_quantity", 0),
                "available": product.get("status") == "active",
                "images": [img.get("src") for img in product.get("images", [])],
                "tags": product.get("tags", "").split(", ") if product.get("tags") else [],
                "handle": product.get("handle", ""),
                "created_at": product.get("created_at"),
                "updated_at": product.get("updated_at")
            }
            formatted.append(formatted_product)
        
        return formatted
    
    def _format_orders(self, orders: List[Dict]) -> List[Dict]:
        """Format orders for consistent API response"""
        formatted = []
        
        for order in orders:
            formatted_order = {
                "id": order.get("id"),
                "order_number": order.get("order_number"),
                "total_price": order.get("total_price"),
                "financial_status": order.get("financial_status"),
                "fulfillment_status": order.get("fulfillment_status"),
                "created_at": order.get("created_at"),
                "updated_at": order.get("updated_at"),
                "line_items": [
                    {
                        "title": item.get("title"),
                        "quantity": item.get("quantity"),
                        "price": item.get("price")
                    }
                    for item in order.get("line_items", [])
                ]
            }
            formatted.append(formatted_order)
        
        return formatted

# OpenAI Integration
class OpenAIIntegration(BaseIntegration):
    def __init__(self, config: OpenAIConfig):
        super().__init__(config)
        self.config: OpenAIConfig = config
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for OpenAI API"""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
    
    async def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            # Ensure session is created
            await self._ensure_session()
            
            url = f"{self.config.base_url}/models"
            async with self.session.get(url, headers=self._get_headers()) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    async def generate_response(self, messages: List[Dict], 
                              max_tokens: int = 150, 
                              temperature: float = 0.7) -> Optional[str]:
        """Generate AI response using OpenAI"""
        try:
            # Ensure session is created
            await self._ensure_session()
            
            url = f"{self.config.base_url}/chat/completions"
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            async with self.session.post(
                url, 
                json=payload, 
                headers=self._get_headers()
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None
    
    async def generate_sbdr_response(self, user_message: str, 
                                   user_context: Dict[str, Any]) -> Optional[str]:
        """Generate SBDR-specific response"""
        system_prompt = self._build_sbdr_system_prompt(user_context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return await self.generate_response(messages, max_tokens=200, temperature=0.7)
    
    async def generate_account_manager_response(self, user_message: str, 
                                              user_context: Dict[str, Any]) -> Optional[str]:
        """Generate Account Manager response"""
        system_prompt = self._build_account_manager_system_prompt(user_context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return await self.generate_response(messages, max_tokens=200, temperature=0.6)
    
    async def generate_customer_success_response(self, user_message: str, 
                                               user_context: Dict[str, Any]) -> Optional[str]:
        """Generate Customer Success response"""
        system_prompt = self._build_customer_success_system_prompt(user_context)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return await self.generate_response(messages, max_tokens=200, temperature=0.5)
    
    def _build_sbdr_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt for SBDR agent"""
        base_prompt = """You are an expert Sales Business Development Representative for TechHub Electronics. 
        Your role is to qualify leads by understanding their needs, budget, and use case.
        
        Be friendly, professional, and focus on:
        1. Understanding customer needs
        2. Qualifying budget and timeline
        3. Identifying the right products
        4. Building rapport for handoff to specialists
        
        Keep responses concise and always ask qualifying questions."""
        
        if context.get("customer_tier") == "prospect":
            base_prompt += "\n\nThis is a new prospect. Focus on qualification."
        
        return base_prompt
    
    def _build_account_manager_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt for Account Manager"""
        base_prompt = """You are a Senior Account Manager for TechHub Electronics.
        You handle qualified leads and existing customers with personalized service.
        
        Focus on:
        1. Providing detailed product recommendations
        2. Handling orders and account issues
        3. Building long-term customer relationships
        4. Offering premium service experience
        
        Be consultative and solution-oriented."""
        
        if context.get("customer_tier") == "vip":
            base_prompt += "\n\nThis is a VIP customer. Provide premium white-glove service."
        
        return base_prompt
    
    def _build_customer_success_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt for Customer Success"""
        return """You are a Customer Success Representative for TechHub Electronics.
        You help existing customers maximize value from their purchases.
        
        Focus on:
        1. Onboarding and product education
        2. Best practices and optimization
        3. Proactive support and guidance
        4. Ensuring customer satisfaction and retention
        
        Be helpful, educational, and proactive in identifying opportunities to help."""

# Integration Manager
class IntegrationManager:
    def __init__(self):
        self.crisp: Optional[CrispIntegration] = None
        self.shopify: Optional[ShopifyIntegration] = None
        self.openai: Optional[OpenAIIntegration] = None
        self._initialized = False
    
    async def initialize(self, crisp_config: Optional[CrispConfig] = None,
                        shopify_config: Optional[ShopifyConfig] = None,
                        openai_config: Optional[OpenAIConfig] = None):
        """Initialize integrations with configurations"""
        if crisp_config:
            self.crisp = CrispIntegration(crisp_config)
        
        if shopify_config:
            self.shopify = ShopifyIntegration(shopify_config)
        
        if openai_config:
            self.openai = OpenAIIntegration(openai_config)
        
        self._initialized = True
    
    async def initialize_from_env(self):
        """Initialize integrations from environment variables"""
        # Crisp configuration
        crisp_id = os.getenv("CRISP_IDENTIFIER")
        crisp_key = os.getenv("CRISP_KEY")
        crisp_website = os.getenv("CRISP_WEBSITE_ID")
        
        if crisp_id and crisp_key and crisp_website:
            crisp_config = CrispConfig(
                identifier=crisp_id,
                key=crisp_key,
                website_id=crisp_website
            )
            self.crisp = CrispIntegration(crisp_config)
        
        # Shopify configuration
        shopify_domain = os.getenv("SHOPIFY_SHOP_DOMAIN")
        shopify_token = os.getenv("SHOPIFY_ACCESS_TOKEN")
        
        if shopify_domain and shopify_token:
            shopify_config = ShopifyConfig(
                shop_domain=shopify_domain,
                access_token=shopify_token
            )
            self.shopify = ShopifyIntegration(shopify_config)
        
        # OpenAI configuration
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if openai_key:
            openai_config = OpenAIConfig(api_key=openai_key)
            self.openai = OpenAIIntegration(openai_config)
        
        self._initialized = True
    
    async def test_all_connections(self) -> Dict[str, bool]:
        """Test all configured integrations"""
        results = {}
        
        if self.crisp:
            async with self.crisp as crisp:
                results["crisp"] = await crisp.test_connection()
        
        if self.shopify:
            async with self.shopify as shopify:
                results["shopify"] = await shopify.test_connection()
        
        if self.openai:
            async with self.openai as openai:
                results["openai"] = await openai.test_connection()
        
        return results
    
    async def send_message_to_crisp(self, session_id: str, message: str) -> bool:
        """Send message to Crisp if configured"""
        if not self.crisp:
            logger.warning("Crisp not configured")
            return False
        
        async with self.crisp as crisp:
            return await crisp.send_message(session_id, message)
    
    async def search_products(self, query: str, product_type: Optional[str] = None) -> List[Dict]:
        """Search products in Shopify if configured"""
        if not self.shopify:
            logger.warning("Shopify not configured")
            return []
        
        async with self.shopify as shopify:
            return await shopify.search_products(query, product_type=product_type)
    
    async def get_customer_orders(self, email: str) -> List[Dict]:
        """Get customer orders from Shopify if configured"""
        if not self.shopify:
            logger.warning("Shopify not configured")
            return []
        
        async with self.shopify as shopify:
            return await shopify.get_customer_orders(email)
    
    async def generate_ai_response(self, agent_type: str, message: str, 
                                 context: Dict[str, Any]) -> Optional[str]:
        """Generate AI response based on agent type"""
        if not self.openai:
            logger.warning("OpenAI not configured")
            return None
        
        async with self.openai as openai:
            if agent_type == "sbdr":
                return await openai.generate_sbdr_response(message, context)
            elif agent_type == "account_manager":
                return await openai.generate_account_manager_response(message, context)
            elif agent_type == "customer_success":
                return await openai.generate_customer_success_response(message, context)
            else:
                # Fallback to basic response
                messages = [
                    {"role": "system", "content": "You are a helpful customer service representative."},
                    {"role": "user", "content": message}
                ]
                return await openai.generate_response(messages)

# Example usage and testing
async def test_integrations():
    """Test integration functionality"""
    print("Testing Multi-Agent SBDR Integrations")
    print("=" * 50)
    
    # Initialize from environment variables
    integration_manager = IntegrationManager()
    await integration_manager.initialize_from_env()
    
    # Test connections
    print("\n🔌 Testing Connections...")
    results = await integration_manager.test_all_connections()
    
    for service, success in results.items():
        status = "✅ Connected" if success else "❌ Failed"
        print(f"  {service.title()}: {status}")
    
    # Test product search if Shopify is configured
    if integration_manager.shopify:
        print("\n🔍 Testing Product Search...")
        products = await integration_manager.search_products("laptop")
        print(f"  Found {len(products)} products")
        if products:
            print(f"  Sample: {products[0]['title']} - ${products[0]['price']}")
    
    # Test AI response generation if OpenAI is configured
    if integration_manager.openai:
        print("\n🤖 Testing AI Response Generation...")
        context = {"customer_tier": "prospect"}
        response = await integration_manager.generate_ai_response(
            "sbdr", 
            "I'm looking for a laptop for work", 
            context
        )
        if response:
            print(f"  AI Response: {response[:100]}...")
    
    print("\n✅ Integration tests completed!")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    asyncio.run(test_integrations())