## System Architecture

The conversational agent system will be built on a three-tiered architecture, with Crisp as the communication layer, N8N as the automation and orchestration layer, and Shopify as the e-commerce data layer. An external AI service will be integrated with N8N for natural language processing.

**1. Communication Layer (Crisp):**
*   **Role:** Serves as the primary interface for customer interactions.
*   **Components:**
    *   **Crisp Chat Widget:** Embedded on the online electronics store website.
    *   **Crisp API/Webhooks:** Captures incoming messages from various channels (website chat, Instagram, WhatsApp) and sends them to N8N for processing. It also receives responses from N8N to be displayed to the user.

**2. Automation and Orchestration Layer (N8N):**
*   **Role:** The core of the system, responsible for managing conversational flows, logic, and integrations.
*   **Components:**
    *   **N8N Workflow:** A visual workflow that orchestrates the entire process.
    *   **Webhook Node:** Receives incoming messages from Crisp.
    *   **HTTP Request Node:** Connects to external AI services for NLP and to the Shopify API for data retrieval.
    *   **Function Node:** Implements custom logic for lead qualification, conversational flow management, and response generation.
    *   **Crisp Node:** Sends responses back to the user via the Crisp API.

**3. E-commerce Data Layer (Shopify):**
*   **Role:** Provides access to product information, order status, and customer data.
*   **Components:**
    *   **Shopify API:** Allows N8N to query for product details, check order statuses, and retrieve customer information.

**4. AI/NLP Layer (External Service):**
*   **Role:** Provides natural language understanding and generation capabilities.
*   **Components:**
    *   **External AI Service (e.g., OpenAI, Google AI):** An API-based service that processes user messages to understand intent, extract entities, and generate human-like responses.

**Data Flow:**
1.  A user sends a message through the Crisp chat widget.
2.  Crisp triggers a webhook, sending the message data to an N8N webhook node.
3.  The N8N workflow is initiated.
4.  The user's message is sent to an external AI service for analysis.
5.  The AI service returns the user's intent and any extracted entities (e.g., product name, order number).
6.  Based on the intent, the N8N workflow follows a specific conversational flow:
    *   **Lead Qualification:** Asks qualifying questions (e.g., budget, product interest).
    *   **Knowledge Base Query:** Retrieves information from a knowledge base (e.g., a Google Sheet or a database connected to N8N).
    *   **Shopify Query:** If the user asks about a product or order, N8N queries the Shopify API for the relevant information.
7.  N8N generates a response based on the processed information.
8.  The response is sent back to the user via the Crisp API.
9.  The conversation context is stored (e.g., in a database) to maintain a seamless interaction.

This architecture provides a scalable and flexible foundation for the conversational agent system, allowing for future expansion with additional agents and more complex capabilities.

