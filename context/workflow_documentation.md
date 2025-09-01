# N8N Workflow Documentation: SBDR Conversational Agent

## Overview
This N8N workflow implements the core logic for the Sales Business Development Representative (SBDR) conversational agent. The workflow is triggered by incoming messages from Crisp and orchestrates the entire conversation flow, from message processing to response generation.

## Workflow Nodes Description

### 1. Crisp Webhook (Trigger Node)
- **Type:** Webhook
- **Purpose:** Receives incoming messages from Crisp via HTTP POST requests
- **Configuration:**
  - HTTP Method: POST
  - Path: `/crisp-webhook`
  - Response Mode: Response Node
- **Output:** Raw webhook data from Crisp containing message content, session ID, website ID, and user information

### 2. Extract Message Data (Function Node)
- **Purpose:** Processes the raw webhook data and extracts relevant information
- **Logic:**
  - Extracts message text, session ID, website ID, user email, and user name
  - Creates a structured conversation context object
  - Handles cases where user information might be missing
- **Output:** Structured conversation context data

### 3. AI Processing (HTTP Request Node)
- **Purpose:** Sends the user's message to an external AI service (OpenAI) for natural language processing
- **Configuration:**
  - URL: `https://api.openai.com/v1/chat/completions`
  - Method: POST
  - Authentication: OpenAI API credentials
  - Model: GPT-3.5-turbo
- **System Prompt:** Defines the SBDR role and behavior guidelines
- **Output:** AI-generated response to the user's message

### 4. Process Intent (Function Node)
- **Purpose:** Analyzes the user's message to determine intent and required actions
- **Logic:**
  - Performs keyword-based intent detection
  - Determines if lead qualification is needed
  - Identifies if product information is required
  - Checks if handoff to human agent is necessary
- **Intent Categories:**
  - `pricing`: Budget-related inquiries
  - `product_inquiry`: Product-specific questions
  - `order_status`: Order and shipping inquiries
  - `handoff_request`: Requests for human assistance
  - `general`: Default category
- **Output:** Enhanced data object with intent classification and action flags

### 5. Qualification Check (IF Node)
- **Purpose:** Routes the workflow based on whether lead qualification is needed
- **Condition:** Checks if `needsQualification` flag is true
- **Branches:**
  - **True:** Routes to qualification questions node
  - **False:** Routes to standard response node

### 6. Add Qualification Questions (Function Node)
- **Purpose:** Enhances the AI response with targeted qualification questions
- **Logic:**
  - Appends relevant qualification questions based on detected intent
  - For product inquiries: Asks about budget, use case, and specific features
  - For pricing inquiries: Asks about product category and budget range
- **Output:** Enhanced response with qualification questions

### 7. Standard Response (Function Node)
- **Purpose:** Passes through the AI response without modification for non-qualification scenarios
- **Output:** Original AI response as the final response

### 8. Send Response to Crisp (HTTP Request Node)
- **Purpose:** Sends the final response back to the user via Crisp API
- **Configuration:**
  - URL: `https://api.crisp.chat/v1/website/{websiteId}/conversation/{sessionId}/message`
  - Method: POST
  - Authentication: Crisp API credentials
- **Payload:**
  - Type: text
  - Content: Final response message
  - From: operator (indicates message is from the business)

### 9. Webhook Response (Respond to Webhook Node)
- **Purpose:** Sends a success response back to Crisp to acknowledge webhook receipt
- **Response:** "Message processed successfully"

## Data Flow
1. **Trigger:** Crisp webhook receives incoming message
2. **Extraction:** Message data is parsed and structured
3. **AI Processing:** User message is analyzed by AI service
4. **Intent Analysis:** Message intent and required actions are determined
5. **Response Routing:** Workflow branches based on qualification needs
6. **Response Enhancement:** Qualification questions are added if needed
7. **Response Delivery:** Final message is sent back to user via Crisp
8. **Acknowledgment:** Success response is sent to Crisp

## Error Handling
- Each HTTP request node should be configured with retry logic
- Function nodes include error handling for missing data
- Fallback responses are provided for unrecognized intents
- Timeout settings should be configured for external API calls

## Configuration Requirements
- **OpenAI API Credentials:** Required for AI processing
- **Crisp API Credentials:** Required for sending responses
- **Webhook URL:** Must be configured in Crisp to point to the N8N webhook endpoint

## Monitoring and Logging
- N8N execution logs will capture all workflow runs
- Consider adding logging nodes for debugging and analytics
- Monitor response times and error rates for optimization

