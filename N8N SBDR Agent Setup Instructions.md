
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
