"""
Comprehensive Testing Framework for SBDR Conversational Agent System
This module provides testing capabilities for all components of the system.
"""

import json
import requests
import time
import unittest
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch
import logging

# Import our SBDR agent logic
from enhanced_sbdr_logic import EnhancedSBDRAgent, Intent, QualificationStatus

class SBDRAgentTestCase(unittest.TestCase):
    """Test cases for the SBDR agent logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = EnhancedSBDRAgent("knowledge_base.json")
        
    def test_intent_detection(self):
        """Test intent detection functionality."""
        test_cases = [
            ("Hello, how are you?", Intent.GREETING),
            ("I'm looking for a laptop", Intent.PRODUCT_INQUIRY),
            ("What's the price of this phone?", Intent.PRICING),
            ("Where is my order?", Intent.ORDER_STATUS),
            ("How long does shipping take?", Intent.SHIPPING),
            ("I need help with my device", Intent.SUPPORT),
            ("Can I speak to a human?", Intent.HANDOFF_REQUEST),
            ("What do you sell?", Intent.GENERAL)
        ]
        
        for message, expected_intent in test_cases:
            with self.subTest(message=message):
                detected_intent = self.agent.detect_intent(message)
                self.assertEqual(detected_intent, expected_intent)
    
    def test_qualification_data_extraction(self):
        """Test extraction of qualification data from messages."""
        test_cases = [
            ("My budget is $1000", {"budget": "1000"}),
            ("I need a laptop for gaming", {"product_interest": "laptops", "use_case": "gaming"}),
            ("Looking for business phone under $800", {"budget": "800", "use_case": "business"}),
            ("I need it for school work", {"use_case": "education"}),
            ("Apple MacBook for creative work", {"use_case": "creative"})
        ]
        
        for message, expected_data in test_cases:
            with self.subTest(message=message):
                extracted = self.agent.extract_qualification_data(message)
                for key, value in expected_data.items():
                    self.assertIn(key, extracted)
                    self.assertEqual(extracted[key], value)
    
    def test_user_profile_management(self):
        """Test user profile creation and updates."""
        session_id = "test_session_1"
        
        # Create new profile
        profile = self.agent.get_or_create_user_profile(session_id, "Test User", "test@example.com")
        self.assertEqual(profile.session_id, session_id)
        self.assertEqual(profile.name, "Test User")
        self.assertEqual(profile.qualification_status, QualificationStatus.NOT_STARTED)
        
        # Update profile with qualification data
        extracted_data = {"budget": "1000", "product_interest": "laptops", "use_case": "business"}
        self.agent.update_user_profile(session_id, extracted_data)
        
        updated_profile = self.agent.user_profiles[session_id]
        self.assertEqual(updated_profile.budget, "1000")
        self.assertEqual(updated_profile.product_interest, "laptops")
        self.assertEqual(updated_profile.use_case, "business")
        self.assertEqual(updated_profile.qualification_status, QualificationStatus.QUALIFIED)
    
    def test_knowledge_base_queries(self):
        """Test knowledge base query functionality."""
        test_queries = [
            ("What's your shipping policy?", "shipping"),
            ("How do returns work?", "return"),
            ("What about warranty?", "warranty"),
            ("Payment methods?", "payment")
        ]
        
        for query, expected_topic in test_queries:
            with self.subTest(query=query):
                response = self.agent.query_knowledge_base(query)
                self.assertIsNotNone(response)
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 10)  # Should be a meaningful response
    
    def test_qualification_questions_generation(self):
        """Test generation of qualification questions."""
        session_id = "test_session_2"
        profile = self.agent.get_or_create_user_profile(session_id)
        
        # Test with empty profile
        questions = self.agent.generate_qualification_questions(profile, Intent.PRODUCT_INQUIRY)
        self.assertGreater(len(questions), 0)
        self.assertLessEqual(len(questions), 2)  # Should limit to 2 questions
        
        # Test with partially filled profile
        profile.budget = "1000"
        questions = self.agent.generate_qualification_questions(profile, Intent.PRODUCT_INQUIRY)
        self.assertGreater(len(questions), 0)
    
    def test_handoff_logic(self):
        """Test handoff decision logic."""
        session_id = "test_session_3"
        profile = self.agent.get_or_create_user_profile(session_id)
        
        # Test explicit handoff request
        self.assertTrue(self.agent.should_handoff(profile, Intent.HANDOFF_REQUEST))
        
        # Test qualified lead handoff
        profile.qualification_status = QualificationStatus.QUALIFIED
        self.assertTrue(self.agent.should_handoff(profile, Intent.GENERAL))
        
        # Test no handoff for unqualified
        profile.qualification_status = QualificationStatus.UNQUALIFIED
        self.assertFalse(self.agent.should_handoff(profile, Intent.GENERAL))
    
    def test_complete_conversation_flow(self):
        """Test a complete conversation flow."""
        session_id = "test_conversation"
        messages = [
            "Hi, I'm looking for a laptop",
            "My budget is around $1200", 
            "I need it for business work",
            "Can you show me some options?"
        ]
        
        for i, message in enumerate(messages):
            ai_response = f"Thank you for message {i+1}"
            result = self.agent.generate_response(session_id, message, ai_response)
            
            # Verify response structure
            self.assertIn('final_response', result)
            self.assertIn('intent', result)
            self.assertIn('qualification_status', result)
            self.assertIn('user_profile', result)
            
            # Verify progression
            if i == 0:
                self.assertEqual(result['intent'], 'greeting')
            elif i == len(messages) - 1:
                # Should be qualified by the end
                self.assertIn(result['qualification_status'], ['qualified', 'completed'])

class CrispIntegrationTest(unittest.TestCase):
    """Test cases for Crisp integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_crisp_config = {
            "api_base_url": "https://api.crisp.chat/v1",
            "test_website_id": "test_website_123",
            "test_session_id": "test_session_456"
        }
    
    @patch('requests.post')
    def test_send_message_to_crisp(self, mock_post):
        """Test sending messages to Crisp API."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"success": True}
        
        # Simulate sending a message
        url = f"{self.mock_crisp_config['api_base_url']}/website/{self.mock_crisp_config['test_website_id']}/conversation/{self.mock_crisp_config['test_session_id']}/message"
        payload = {
            "type": "text",
            "content": "Hello! How can I help you today?",
            "from": "operator"
        }
        
        response = requests.post(url, json=payload)
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(url, json=payload)
        self.assertEqual(response.status_code, 200)
    
    def test_webhook_payload_parsing(self):
        """Test parsing of Crisp webhook payloads."""
        sample_webhook_payload = {
            "event": "message:send",
            "data": {
                "website_id": "test_website_123",
                "session_id": "test_session_456",
                "content": "Hello, I need help",
                "type": "text",
                "user": {
                    "nickname": "John Doe",
                    "email": "john@example.com"
                }
            }
        }
        
        # Extract data as would be done in N8N
        message_text = sample_webhook_payload["data"]["content"]
        session_id = sample_webhook_payload["data"]["session_id"]
        website_id = sample_webhook_payload["data"]["website_id"]
        user_email = sample_webhook_payload["data"]["user"]["email"]
        
        self.assertEqual(message_text, "Hello, I need help")
        self.assertEqual(session_id, "test_session_456")
        self.assertEqual(website_id, "test_website_123")
        self.assertEqual(user_email, "john@example.com")

class ShopifyIntegrationTest(unittest.TestCase):
    """Test cases for Shopify integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_shopify_config = {
            "api_base_url": "https://test-shop.myshopify.com/admin/api/2023-10",
            "access_token": "test_token_123"
        }
    
    @patch('requests.get')
    def test_product_search(self, mock_get):
        """Test product search functionality."""
        mock_response_data = {
            "products": [
                {
                    "id": 123456789,
                    "title": "MacBook Pro 13-inch",
                    "product_type": "laptop",
                    "vendor": "Apple",
                    "variants": [
                        {
                            "id": 987654321,
                            "price": "1299.00",
                            "inventory_quantity": 10
                        }
                    ]
                }
            ]
        }
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data
        
        # Simulate product search
        url = f"{self.mock_shopify_config['api_base_url']}/products.json"
        params = {"product_type": "laptop", "limit": "10"}
        headers = {"X-Shopify-Access-Token": self.mock_shopify_config['access_token']}
        
        response = requests.get(url, params=params, headers=headers)
        
        # Verify the request
        mock_get.assert_called_once_with(url, params=params, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # Verify response data
        data = response.json()
        self.assertIn("products", data)
        self.assertEqual(len(data["products"]), 1)
        self.assertEqual(data["products"][0]["title"], "MacBook Pro 13-inch")
    
    def test_product_data_mapping(self):
        """Test mapping of Shopify product data."""
        shopify_product = {
            "id": 123456789,
            "title": "iPhone 15 Pro",
            "product_type": "smartphone",
            "vendor": "Apple",
            "body_html": "<p>Latest iPhone with advanced features</p>",
            "variants": [
                {
                    "id": 987654321,
                    "price": "999.00",
                    "inventory_quantity": 25
                }
            ],
            "images": [
                {
                    "src": "https://example.com/iphone15pro.jpg"
                }
            ]
        }
        
        # Map to our internal format
        mapped_product = {
            "id": shopify_product["id"],
            "name": shopify_product["title"],
            "price": shopify_product["variants"][0]["price"],
            "availability": shopify_product["variants"][0]["inventory_quantity"],
            "category": shopify_product["product_type"],
            "brand": shopify_product["vendor"],
            "image": shopify_product["images"][0]["src"] if shopify_product["images"] else None
        }
        
        self.assertEqual(mapped_product["name"], "iPhone 15 Pro")
        self.assertEqual(mapped_product["price"], "999.00")
        self.assertEqual(mapped_product["availability"], 25)
        self.assertEqual(mapped_product["category"], "smartphone")

class N8NWorkflowTest(unittest.TestCase):
    """Test cases for N8N workflow functionality."""
    
    def test_workflow_structure(self):
        """Test the structure of the N8N workflow."""
        with open('enhanced_n8n_workflow.json', 'r') as f:
            workflow = json.load(f)
        
        # Verify essential nodes exist
        node_names = [node['name'] for node in workflow['nodes']]
        required_nodes = [
            'Crisp Webhook',
            'Extract Message Data',
            'AI Processing',
            'Enhanced Processing',
            'Send Response to Crisp'
        ]
        
        for required_node in required_nodes:
            self.assertIn(required_node, node_names)
        
        # Verify connections exist
        self.assertIn('connections', workflow)
        self.assertGreater(len(workflow['connections']), 0)
    
    def test_function_node_code(self):
        """Test that function node code is syntactically valid."""
        with open('enhanced_n8n_workflow.json', 'r') as f:
            workflow = json.load(f)
        
        function_nodes = [
            node for node in workflow['nodes'] 
            if node['type'] == 'n8n-nodes-base.function'
        ]
        
        for node in function_nodes:
            function_code = node['parameters']['functionCode']
            
            # Basic syntax check - should not raise SyntaxError
            try:
                compile(function_code, '<string>', 'exec')
            except SyntaxError as e:
                self.fail(f"Syntax error in function node '{node['name']}': {e}")

class IntegrationTest(unittest.TestCase):
    """End-to-end integration tests."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.agent = EnhancedSBDRAgent("knowledge_base.json")
        
    def test_complete_customer_journey(self):
        """Test a complete customer journey from greeting to qualification."""
        session_id = "integration_test_session"
        
        # Customer journey steps
        journey_steps = [
            {
                "message": "Hi there!",
                "expected_intent": "greeting",
                "should_have_questions": True
            },
            {
                "message": "I'm looking for a laptop for work",
                "expected_intent": "product_inquiry",
                "should_have_questions": True
            },
            {
                "message": "My budget is around $1500",
                "expected_intent": "pricing",
                "should_have_questions": True
            },
            {
                "message": "I need it for business presentations and some design work",
                "expected_intent": "general",
                "should_have_questions": False
            }
        ]
        
        for i, step in enumerate(journey_steps):
            ai_response = f"Thank you for your message: {step['message']}"
            result = self.agent.generate_response(session_id, step['message'], ai_response)
            
            # Verify intent detection
            self.assertEqual(result['intent'], step['expected_intent'])
            
            # Verify qualification progression
            if i == 0:
                self.assertEqual(result['qualification_status'], 'in_progress')
            elif i == len(journey_steps) - 1:
                self.assertIn(result['qualification_status'], ['qualified', 'completed'])
            
            # Verify response contains questions when expected
            if step['should_have_questions']:
                self.assertTrue('?' in result['final_response'])
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        session_id = "error_test_session"
        
        # Test with empty message
        result = self.agent.generate_response(session_id, "", "AI response")
        self.assertIsNotNone(result['final_response'])
        
        # Test with very long message
        long_message = "test " * 1000
        result = self.agent.generate_response(session_id, long_message, "AI response")
        self.assertIsNotNone(result['final_response'])
        
        # Test with special characters
        special_message = "Hello! @#$%^&*()_+ 测试 🚀"
        result = self.agent.generate_response(session_id, special_message, "AI response")
        self.assertIsNotNone(result['final_response'])

class PerformanceTest(unittest.TestCase):
    """Performance tests for the system."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.agent = EnhancedSBDRAgent("knowledge_base.json")
    
    def test_response_time(self):
        """Test response time for typical operations."""
        session_id = "performance_test_session"
        message = "I'm looking for a laptop under $1000"
        ai_response = "I can help you find a laptop in your budget."
        
        start_time = time.time()
        result = self.agent.generate_response(session_id, message, ai_response)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Response should be generated within 100ms (excluding AI API call)
        self.assertLess(response_time, 0.1)
        self.assertIsNotNone(result['final_response'])
    
    def test_concurrent_sessions(self):
        """Test handling multiple concurrent sessions."""
        import threading
        
        results = []
        
        def process_session(session_id):
            message = f"Hello from session {session_id}"
            ai_response = f"Response for session {session_id}"
            result = self.agent.generate_response(session_id, message, ai_response)
            results.append((session_id, result))
        
        # Create 10 concurrent sessions
        threads = []
        for i in range(10):
            thread = threading.Thread(target=process_session, args=(f"session_{i}",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all sessions were processed
        self.assertEqual(len(results), 10)
        
        # Verify each session has unique data
        session_ids = [result[0] for result in results]
        self.assertEqual(len(set(session_ids)), 10)  # All unique

def run_all_tests():
    """Run all test suites."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        SBDRAgentTestCase,
        CrispIntegrationTest,
        ShopifyIntegrationTest,
        N8NWorkflowTest,
        IntegrationTest,
        PerformanceTest
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    print("Running SBDR Agent System Tests...")
    print("=" * 50)
    
    # Run all tests
    test_result = run_all_tests()
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Tests run: {test_result.testsRun}")
    print(f"Failures: {len(test_result.failures)}")
    print(f"Errors: {len(test_result.errors)}")
    
    if test_result.failures:
        print("\nFailures:")
        for test, traceback in test_result.failures:
            print(f"- {test}: {traceback}")
    
    if test_result.errors:
        print("\nErrors:")
        for test, traceback in test_result.errors:
            print(f"- {test}: {traceback}")
    
    if test_result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed. Please review the output above.")

