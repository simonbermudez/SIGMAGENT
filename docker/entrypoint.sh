#!/bin/bash
set -e

echo "🚀 Starting Multi-Agent SBDR System..."

# Function to check if required environment variables are set
check_env_vars() {
    local required_vars=("OPENAI_API_KEY")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "⚠️  Warning: Missing environment variables: ${missing_vars[*]}"
        echo "   The system will run in demo mode with limited functionality."
    fi
}

# Function to wait for external services
wait_for_services() {
    echo "🔍 Checking external service connectivity..."
    
    # Check OpenAI API if key is provided
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "   Testing OpenAI API connection..."
        python -c "
import asyncio
import os
from multiagent_integrations import OpenAIIntegration, OpenAIConfig

async def test_openai():
    config = OpenAIConfig(api_key=os.getenv('OPENAI_API_KEY'))
    integration = OpenAIIntegration(config)
    async with integration as client:
        result = await client.test_connection()
        print(f'   OpenAI API: {'✅ Connected' if result else '❌ Failed'}')

asyncio.run(test_openai())
" 2>/dev/null || echo "   OpenAI API: ❌ Connection failed"
    fi
    
    # Check Shopify API if configured
    if [ -n "$SHOPIFY_SHOP_DOMAIN" ] && [ -n "$SHOPIFY_ACCESS_TOKEN" ]; then
        echo "   Testing Shopify API connection..."
        python -c "
import asyncio
import os
from multiagent_integrations import ShopifyIntegration, ShopifyConfig

async def test_shopify():
    config = ShopifyConfig(
        shop_domain=os.getenv('SHOPIFY_SHOP_DOMAIN'),
        access_token=os.getenv('SHOPIFY_ACCESS_TOKEN')
    )
    integration = ShopifyIntegration(config)
    async with integration as client:
        result = await client.test_connection()
        print(f'   Shopify API: {'✅ Connected' if result else '❌ Failed'}')

asyncio.run(test_shopify())
" 2>/dev/null || echo "   Shopify API: ❌ Connection failed"
    fi
    
    # Check Crisp API if configured  
    if [ -n "$CRISP_IDENTIFIER" ] && [ -n "$CRISP_KEY" ]; then
        echo "   Testing Crisp API connection..."
        python -c "
import asyncio
import os
from multiagent_integrations import CrispIntegration, CrispConfig

async def test_crisp():
    config = CrispConfig(
        identifier=os.getenv('CRISP_IDENTIFIER'),
        key=os.getenv('CRISP_KEY'),
        website_id=os.getenv('CRISP_WEBSITE_ID', 'test')
    )
    integration = CrispIntegration(config)
    async with integration as client:
        result = await client.test_connection()
        print(f'   Crisp API: {'✅ Connected' if result else '❌ Failed'}')

asyncio.run(test_crisp())
" 2>/dev/null || echo "   Crisp API: ❌ Connection failed"
    fi
}

# Function to run system health checks
run_health_checks() {
    echo "🏥 Running system health checks..."
    
    # Test core system components
    python -c "
import asyncio
from multiagent_sbdr_system import AgentOrchestrator

async def health_check():
    try:
        orchestrator = AgentOrchestrator()
        
        # Test basic functionality
        result = await orchestrator.process_message(
            session_id='health_check',
            message_content='Hello, this is a health check'
        )
        
        if result and 'response' in result:
            print('   Core System: ✅ Healthy')
            return True
        else:
            print('   Core System: ❌ Unhealthy')
            return False
    except Exception as e:
        print(f'   Core System: ❌ Error - {e}')
        return False

asyncio.run(health_check())
" || {
        echo "❌ Health check failed!"
        exit 1
    }
}

# Function to display system information
display_system_info() {
    echo "📋 System Information:"
    echo "   Python Version: $(python --version)"
    echo "   Working Directory: $(pwd)"
    echo "   User: $(whoami)"
    echo "   Available Memory: $(free -h 2>/dev/null | grep Mem | awk '{print $7}' || echo 'N/A')"
    echo "   System Load: $(uptime 2>/dev/null | awk -F'load average:' '{print $2}' || echo 'N/A')"
}

# Main execution
main() {
    echo "=================================================="
    echo "🤖 Multi-Agent SBDR System Container Starting"
    echo "=================================================="
    
    # Display system info
    display_system_info
    echo ""
    
    # Check environment variables
    check_env_vars
    echo ""
    
    # Wait for and test external services
    wait_for_services
    echo ""
    
    # Run health checks
    run_health_checks
    echo ""
    
    echo "=================================================="
    echo "✅ System initialization complete!"
    echo "🚀 Starting application..."
    echo "=================================================="
    
    # Execute the main command
    exec "$@"
}

# Handle signals gracefully
cleanup() {
    echo ""
    echo "🛑 Received shutdown signal..."
    echo "🧹 Cleaning up processes..."
    # Add any cleanup logic here
    echo "✅ Cleanup complete"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Run main function
main "$@"