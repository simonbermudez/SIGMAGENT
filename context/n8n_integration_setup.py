"""
N8N Integration Setup Script
This script provides helper functions and configurations for setting up
the N8N workflow with proper credentials and node configurations.
"""

import json
import os
from typing import Dict, List, Any, Optional

class N8NIntegrationSetup:
    def __init__(self):
        self.credentials = {}
        self.workflow_config = {}
        
    def load_config_files(self):
        """Load all configuration files."""
        config_files = [
            "crisp_integration_config.json",
            "shopify_integration_config.json",
            "knowledge_base.json"
        ]
        
        configs = {}
        for file_name in config_files:
            try:
                with open(file_name, 'r') as f:
                    configs[file_name.replace('.json', '')] = json.load(f)
            except FileNotFoundError:
                print(f"Warning: {file_name} not found")
                
        return configs
    
    def generate_n8n_credentials(self) -> Dict[str, Any]:
        """Generate N8N credential configurations."""
        return {
            "crisp_api": {
                "name": "Crisp API",
                "type": "crispApi",
                "data": {
                    "identifier": "${CRISP_IDENTIFIER}",
                    "key": "${CRISP_KEY}"
                }
            },
            "shopify_api": {
                "name": "Shopify API", 
                "type": "shopifyApi",
                "data": {
                    "shopSubdomain": "${SHOPIFY_SHOP_NAME}",
                    "accessToken": "${SHOPIFY_ACCESS_TOKEN}"
                }
            },
            "openai_api": {
                "name": "OpenAI API",
                "type": "openAiApi", 
                "data": {
                    "apiKey": "${OPENAI_API_KEY}"
                }
            }
        }
    
    def generate_enhanced_workflow(self) -> Dict[str, Any]:
        """Generate enhanced N8N workflow with Shopify integration."""
        return {
            "name": "Enhanced SBDR Conversational Agent",
            "nodes": [
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "crisp-webhook",
                        "responseMode": "responseNode",
                        "options": {}
                    },
                    "id": "webhook-crisp",
                    "name": "Crisp Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [240, 300]
                },
                {
                    "parameters": {
                        "functionCode": self._get_extract_message_function()
                    },
                    "id": "extract-message-data",
                    "name": "Extract Message Data",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [460, 300]
                },
                {
                    "parameters": {
                        "url": "https://api.openai.com/v1/chat/completions",
                        "authentication": "predefinedCredentialType",
                        "nodeCredentialType": "openAiApi",
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": [
                                {"name": "Content-Type", "value": "application/json"}
                            ]
                        },
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {"name": "model", "value": "gpt-3.5-turbo"},
                                {"name": "messages", "value": "=[{\"role\": \"system\", \"content\": \"You are an SBDR for TechHub Electronics. Respond professionally and helpfully to customer inquiries. Keep responses concise and focused on understanding customer needs.\"}, {\"role\": \"user\", \"content\": \"{{ $json.messageText }}\"}]"},
                                {"name": "max_tokens", "value": 150},
                                {"name": "temperature", "value": 0.7}
                            ]
                        }
                    },
                    "id": "ai-processing",
                    "name": "AI Processing",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [680, 300]
                },
                {
                    "parameters": {
                        "functionCode": self._get_enhanced_processing_function()
                    },
                    "id": "enhanced-processing",
                    "name": "Enhanced Processing",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [900, 300]
                },
                {
                    "parameters": {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "id": "product-query",
                                    "leftValue": "={{ $json.needsProductInfo }}",
                                    "rightValue": True,
                                    "operator": {"type": "boolean", "operation": "equal"}
                                }
                            ],
                            "combinator": "and"
                        }
                    },
                    "id": "product-query-check",
                    "name": "Product Query Check",
                    "type": "n8n-nodes-base.if",
                    "typeVersion": 2,
                    "position": [1120, 300]
                },
                {
                    "parameters": {
                        "url": "https://{{ $('extract-message-data').item.json.shopName }}.myshopify.com/admin/api/2023-10/products.json",
                        "authentication": "predefinedCredentialType",
                        "nodeCredentialType": "shopifyApi",
                        "sendQuery": True,
                        "queryParameters": {
                            "parameters": [
                                {"name": "limit", "value": "10"},
                                {"name": "product_type", "value": "={{ $json.productCategory }}"},
                                {"name": "status", "value": "active"}
                            ]
                        }
                    },
                    "id": "shopify-product-query",
                    "name": "Shopify Product Query",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [1340, 200]
                },
                {
                    "parameters": {
                        "functionCode": self._get_response_generation_function()
                    },
                    "id": "generate-final-response",
                    "name": "Generate Final Response",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [1560, 300]
                },
                {
                    "parameters": {
                        "url": "https://api.crisp.chat/v1/website/{{ $('extract-message-data').item.json.websiteId }}/conversation/{{ $('extract-message-data').item.json.sessionId }}/message",
                        "authentication": "predefinedCredentialType",
                        "nodeCredentialType": "crispApi",
                        "sendHeaders": True,
                        "headerParameters": {
                            "parameters": [
                                {"name": "Content-Type", "value": "application/json"}
                            ]
                        },
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {"name": "type", "value": "text"},
                                {"name": "content", "value": "={{ $json.finalResponse }}"},
                                {"name": "from", "value": "operator"}
                            ]
                        }
                    },
                    "id": "send-response",
                    "name": "Send Response to Crisp",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 3,
                    "position": [1780, 300]
                },
                {
                    "parameters": {
                        "conditions": {
                            "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                            "conditions": [
                                {
                                    "id": "handoff-needed",
                                    "leftValue": "={{ $json.needsHandoff }}",
                                    "rightValue": True,
                                    "operator": {"type": "boolean", "operation": "equal"}
                                }
                            ],
                            "combinator": "and"
                        }
                    },
                    "id": "handoff-check",
                    "name": "Handoff Check",
                    "type": "n8n-nodes-base.if",
                    "typeVersion": 2,
                    "position": [2000, 300]
                },
                {
                    "parameters": {
                        "functionCode": self._get_handoff_notification_function()
                    },
                    "id": "notify-human-agent",
                    "name": "Notify Human Agent",
                    "type": "n8n-nodes-base.function",
                    "typeVersion": 1,
                    "position": [2220, 200]
                },
                {
                    "parameters": {
                        "respondWith": "text",
                        "responseBody": "Message processed successfully"
                    },
                    "id": "webhook-response",
                    "name": "Webhook Response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "typeVersion": 1,
                    "position": [2220, 400]
                }
            ],
            "connections": self._get_workflow_connections()
        }
    
    def _get_extract_message_function(self) -> str:
        """Get the message extraction function code."""
        return """
// Extract and structure message data from Crisp webhook
const webhookData = items[0].json;
const messageData = webhookData.data;

// Extract basic message information
const messageText = messageData.content || '';
const sessionId = messageData.session_id;
const websiteId = messageData.website_id;
const userEmail = messageData.user?.email || null;
const userName = messageData.user?.nickname || 'Guest';

// Extract additional context
const userAgent = messageData.user?.user_agent || '';
const referrer = messageData.user?.referrer || '';
const currentUrl = messageData.user?.current_url || '';

// Store conversation context
const conversationContext = {
  sessionId: sessionId,
  websiteId: websiteId,
  userEmail: userEmail,
  userName: userName,
  messageText: messageText,
  userAgent: userAgent,
  referrer: referrer,
  currentUrl: currentUrl,
  timestamp: new Date().toISOString(),
  shopName: 'your-shop-name' // Replace with actual shop name
};

return [{
  json: conversationContext
}];
"""
    
    def _get_enhanced_processing_function(self) -> str:
        """Get the enhanced processing function code."""
        return """
// Enhanced processing with SBDR agent logic
const aiResponse = items[0].json.choices[0].message.content;
const conversationData = items[0].json;

// Import SBDR agent logic (simplified version for N8N)
const messageText = conversationData.messageText.toLowerCase();

// Intent detection
let intent = 'general';
let needsQualification = false;
let needsProductInfo = false;
let needsHandoff = false;
let productCategory = null;

// Enhanced intent detection
if (messageText.includes('hello') || messageText.includes('hi') || messageText.includes('hey')) {
  intent = 'greeting';
  needsQualification = true;
} else if (messageText.includes('laptop') || messageText.includes('computer')) {
  intent = 'product_inquiry';
  needsProductInfo = true;
  needsQualification = true;
  productCategory = 'laptop';
} else if (messageText.includes('phone') || messageText.includes('smartphone')) {
  intent = 'product_inquiry';
  needsProductInfo = true;
  needsQualification = true;
  productCategory = 'smartphone';
} else if (messageText.includes('price') || messageText.includes('cost') || messageText.includes('budget')) {
  intent = 'pricing';
  needsQualification = true;
} else if (messageText.includes('order') || messageText.includes('shipping')) {
  intent = 'order_status';
} else if (messageText.includes('human') || messageText.includes('agent')) {
  intent = 'handoff_request';
  needsHandoff = true;
}

// Extract qualification data
const budgetMatch = messageText.match(/\\$?(\\d+(?:,\\d{3})*)/);
const budget = budgetMatch ? budgetMatch[1] : null;

// Prepare enhanced response data
const responseData = {
  sessionId: conversationData.sessionId,
  websiteId: conversationData.websiteId,
  aiResponse: aiResponse,
  intent: intent,
  needsQualification: needsQualification,
  needsProductInfo: needsProductInfo,
  needsHandoff: needsHandoff,
  productCategory: productCategory,
  extractedBudget: budget,
  originalMessage: conversationData.messageText,
  userName: conversationData.userName,
  userEmail: conversationData.userEmail
};

return [{
  json: responseData
}];
"""
    
    def _get_response_generation_function(self) -> str:
        """Get the response generation function code."""
        return """
// Generate final response with qualification questions and product info
const data = items[0].json;
let finalResponse = data.aiResponse;

// Add product information if available
if (data.needsProductInfo && items[1] && items[1].json && items[1].json.products) {
  const products = items[1].json.products.slice(0, 3); // Top 3 products
  if (products.length > 0) {
    finalResponse += "\\n\\nHere are some popular " + data.productCategory + " options:\\n";
    products.forEach((product, index) => {
      const price = product.variants && product.variants[0] ? product.variants[0].price : 'N/A';
      finalResponse += `${index + 1}. ${product.title} - $${price}\\n`;
    });
  }
}

// Add qualification questions if needed
if (data.needsQualification && !data.needsHandoff) {
  const questions = [];
  
  if (!data.extractedBudget) {
    questions.push("What's your approximate budget for this purchase?");
  }
  
  if (data.intent === 'product_inquiry' && data.productCategory) {
    questions.push(`What will you primarily use the ${data.productCategory} for?`);
  } else if (data.intent === 'greeting') {
    questions.push("Are you looking for any particular type of product today?");
  }
  
  if (questions.length > 0) {
    finalResponse += "\\n\\n" + questions.slice(0, 2).join("\\n");
  }
}

// Add handoff message if needed
if (data.needsHandoff) {
  finalResponse += "\\n\\nI'll connect you with one of our product specialists who can provide more detailed assistance.";
}

return [{
  json: {
    ...data,
    finalResponse: finalResponse
  }
}];
"""
    
    def _get_handoff_notification_function(self) -> str:
        """Get the handoff notification function code."""
        return """
// Notify human agents about qualified leads or handoff requests
const data = items[0].json;

// Prepare notification data
const notification = {
  type: 'agent_handoff',
  priority: data.intent === 'handoff_request' ? 'high' : 'medium',
  session_id: data.sessionId,
  customer_info: {
    name: data.userName,
    email: data.userEmail,
    budget: data.extractedBudget,
    product_interest: data.productCategory,
    intent: data.intent
  },
  conversation_summary: {
    last_message: data.originalMessage,
    ai_response: data.aiResponse
  },
  timestamp: new Date().toISOString()
};

// In a real implementation, this would send to:
// - Slack channel
// - Email notification
// - CRM system
// - Internal dashboard

console.log('Handoff notification:', JSON.stringify(notification, null, 2));

return [{
  json: notification
}];
"""
    
    def _get_workflow_connections(self) -> Dict[str, Any]:
        """Get workflow node connections."""
        return {
            "Crisp Webhook": {
                "main": [[{"node": "Extract Message Data", "type": "main", "index": 0}]]
            },
            "Extract Message Data": {
                "main": [[{"node": "AI Processing", "type": "main", "index": 0}]]
            },
            "AI Processing": {
                "main": [[{"node": "Enhanced Processing", "type": "main", "index": 0}]]
            },
            "Enhanced Processing": {
                "main": [[{"node": "Product Query Check", "type": "main", "index": 0}]]
            },
            "Product Query Check": {
                "main": [
                    [{"node": "Shopify Product Query", "type": "main", "index": 0}],
                    [{"node": "Generate Final Response", "type": "main", "index": 0}]
                ]
            },
            "Shopify Product Query": {
                "main": [[{"node": "Generate Final Response", "type": "main", "index": 1}]]
            },
            "Generate Final Response": {
                "main": [[{"node": "Send Response to Crisp", "type": "main", "index": 0}]]
            },
            "Send Response to Crisp": {
                "main": [[{"node": "Handoff Check", "type": "main", "index": 0}]]
            },
            "Handoff Check": {
                "main": [
                    [{"node": "Notify Human Agent", "type": "main", "index": 0}],
                    [{"node": "Webhook Response", "type": "main", "index": 0}]
                ]
            },
            "Notify Human Agent": {
                "main": [[{"node": "Webhook Response", "type": "main", "index": 0}]]
            }
        }
    
    def generate_environment_variables(self) -> str:
        """Generate environment variables template."""
        return """
# N8N Environment Variables for SBDR Agent

# Crisp Integration
CRISP_IDENTIFIER=your_crisp_identifier_here
CRISP_KEY=your_crisp_api_key_here

# Shopify Integration  
SHOPIFY_SHOP_NAME=your-shop-name
SHOPIFY_ACCESS_TOKEN=your_shopify_access_token_here
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret_here

# OpenAI Integration
OPENAI_API_KEY=your_openai_api_key_here

# N8N Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your_secure_password_here

# Database (if using external database)
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=localhost
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n_user
DB_POSTGRESDB_PASSWORD=n8n_password

# Webhook URLs
WEBHOOK_BASE_URL=https://your-n8n-instance.com
"""
    
    def generate_setup_instructions(self) -> str:
        """Generate setup instructions."""
        return """
# N8N SBDR Agent Setup Instructions

## Prerequisites
1. N8N instance (self-hosted or cloud)
2. Crisp account with API access
3. Shopify store with private app access
4. OpenAI API key

## Setup Steps

### 1. Configure N8N Credentials
- Go to N8N Settings > Credentials
- Add the following credential types:
  - Crisp API (identifier and key)
  - Shopify API (shop subdomain and access token)
  - OpenAI API (API key)

### 2. Import Workflow
- Copy the enhanced workflow JSON
- Import into N8N via Settings > Import from JSON
- Configure all credential references

### 3. Configure Crisp Webhooks
- Login to Crisp dashboard
- Go to Settings > Integrations
- Add webhook pointing to: https://your-n8n-instance.com/webhook/crisp-webhook
- Enable events: message:send, session:created

### 4. Configure Shopify (if needed)
- Create private app in Shopify admin
- Grant necessary permissions:
  - Products: read
  - Orders: read
  - Customers: read
- Copy access token to N8N credentials

### 5. Test the Integration
- Send test message through Crisp chat
- Verify N8N workflow executes
- Check response is sent back to Crisp
- Monitor execution logs for errors

### 6. Deploy and Monitor
- Activate the workflow
- Monitor performance and error rates
- Set up alerts for failed executions
- Regularly review conversation quality

## Troubleshooting
- Check N8N execution logs for errors
- Verify all credentials are correctly configured
- Test webhook endpoints manually
- Ensure proper network connectivity between services
"""

# Example usage
if __name__ == "__main__":
    setup = N8NIntegrationSetup()
    
    # Generate all configuration files
    credentials = setup.generate_n8n_credentials()
    workflow = setup.generate_enhanced_workflow()
    env_vars = setup.generate_environment_variables()
    instructions = setup.generate_setup_instructions()
    
    # Save configurations
    with open('n8n_credentials.json', 'w') as f:
        json.dump(credentials, f, indent=2)
    
    with open('enhanced_n8n_workflow.json', 'w') as f:
        json.dump(workflow, f, indent=2)
    
    with open('environment_variables.env', 'w') as f:
        f.write(env_vars)
    
    with open('setup_instructions.md', 'w') as f:
        f.write(instructions)
    
    print("N8N integration files generated successfully!")
    print("Files created:")
    print("- n8n_credentials.json")
    print("- enhanced_n8n_workflow.json") 
    print("- environment_variables.env")
    print("- setup_instructions.md")

