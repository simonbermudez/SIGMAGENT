
## Crisp API and Webhook Capabilities

Crisp offers comprehensive API and webhook capabilities essential for building a conversational agent system. 

**Key Webhooks for Incoming Messages:**
* Crisp's Web Hooks (V1) allow developers to receive real-time events via HTTP POST requests. 
* The `message:send` event is triggered when a message is received from a user. This will be the primary trigger for our N8N workflow.
* Other relevant events include `session:created`, `session:updated`, and `message:updated`.

**Crisp REST API for Sending Responses:**
* The Crisp REST API (V1) enables sending messages back to users, managing conversations, and updating visitor information.
* Key API endpoints for our use case will include:
    * `/v1/website/{website_id}/conversation/{session_id}/message` to send messages within a conversation.
    * `/v1/website/{website_id}/visitor/{session_id}` to update visitor data, which can be used for lead qualification.

These capabilities will allow the N8N workflow to capture incoming messages from Crisp, process them, and send automated responses back to the user, forming the core of the conversational agent.

