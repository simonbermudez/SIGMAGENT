## SBDR Conversational Flows

The Sales Business Development Representative (SBDR) agent is designed to provide immediate responses, qualify leads, and offer basic information. The conversational flows are structured to guide the user through a qualification process while maintaining a natural and human-like interaction.

**1. Greeting and Initial Engagement:**
*   **Trigger:** Any incoming message from a new or returning user.
*   **Agent Action:**
    *   **Initial Greeting:** "Hello! Welcome to [Store Name]! How can I assist you today? Are you looking for something specific, or just browsing?"
    *   **Intent Recognition:** The AI/NLP module will analyze the user's initial message to determine their intent (e.g., product inquiry, order status, general question).
*   **Fallback:** If intent is unclear, the agent will ask clarifying questions: "I'm not sure I understand. Could you please rephrase your question or tell me more about what you're looking for?"

**2. Qualifying Questions with Branched Logic:**
*   **Purpose:** To gather information about the user's needs, budget, and product interest to qualify them as a lead.
*   **Flow:**
    *   **Product Interest:** If the user expresses interest in a product category (e.g., "I'm looking for a new laptop"), the agent will ask:
        *   "Great! To help me find the perfect [product category] for you, could you tell me what your primary use for it will be (e.g., gaming, work, casual browsing)?"
        *   **Budget Inquiry:** "And what's your approximate budget for this purchase?"
    *   **Specific Product Inquiry:** If the user mentions a specific product (e.g., "Tell me about the XYZ laptop"), the agent will:
        *   Provide basic information from the knowledge base.
        *   Then, attempt to qualify: "Is there a particular feature or specification you're most interested in with the [product name]?"
    *   **General Inquiry:** If the user has a general question not related to a specific product or order, the agent will attempt to answer from the knowledge base and then try to pivot to qualification: "Is there anything else I can help you with today, perhaps related to finding a product that suits your needs?"
*   **Branched Logic:** The flow will adapt based on user responses. For example, if a user states a budget, subsequent product recommendations can be filtered accordingly.

**3. Knowledge Base Query Handling:**
*   **Purpose:** To provide quick and accurate answers to frequently asked questions.
*   **Flow:**
    *   **Keyword/Intent Matching:** The AI/NLP module will identify keywords and intents related to common questions (e.g., "shipping policy," "return process," "warranty").
    *   **Information Retrieval:** N8N will query the pre-defined knowledge base (e.g., a Google Sheet or a simple database) for the relevant answer.
    *   **Agent Response:** "Certainly! Our shipping policy states that [knowledge base answer]. Is there anything else I can clarify for you?"
*   **Fallback:** If the information is not found in the knowledge base, the agent will state: "I apologize, I don't have that information readily available. Would you like me to connect you with a human agent who can assist you further?"

**4. Handoff to Human Agents:**
*   **Purpose:** To ensure complex or sensitive queries are handled by a human, or when the agent cannot qualify the lead effectively.
*   **Triggers for Handoff:**
    *   User explicitly requests to speak to a human.
    *   Agent fails to understand the user's intent after multiple attempts.
    *   User's query is outside the scope of the SBDR agent's knowledge base or qualification criteria.
    *   User is highly qualified and requires immediate attention from a sales representative.
*   **Agent Action:** "I understand. I'll connect you with one of our sales representatives who can provide more detailed assistance. Please hold while I transfer you." (N8N will trigger a notification to the human agent team via Crisp or another internal tool, passing along the conversation history and any collected qualification data.)

**Conversation Context and Memory:**
*   N8N will manage conversation context by storing relevant information (e.g., user's name, product interest, budget, previous questions) in a temporary database or within the N8N workflow's execution data. This ensures that the agent can refer back to previous parts of the conversation for a more natural interaction.

