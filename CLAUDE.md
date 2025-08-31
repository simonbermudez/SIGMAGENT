# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a Sales Business Development Representative (SBDR) conversational agent system designed for online electronics stores. The system integrates Shopify, Crisp, and N8N to create an automated customer engagement platform that qualifies leads and hands off prospects to human sales representatives.

## System Architecture

The system employs a microservices architecture with four main layers:

1. **Communication Layer (Crisp)**: Multi-channel customer interface (web chat, Instagram, WhatsApp)
2. **Orchestration Layer (N8N)**: Workflow automation and business logic engine  
3. **Intelligence Layer (AI Services)**: Natural language processing using OpenAI GPT models
4. **Data Layer (Shopify + Knowledge Base)**: E-commerce platform integration and FAQ storage

## Core Components

### Python Modules
- `enhanced_sbdr_logic.py`: Main SBDR agent logic with intent detection, qualification scoring, and conversation management
- `sbdr_agent_logic.py`: Basic version of the SBDR agent
- `testing_framework.py`: Comprehensive test suites for all system components
- `n8n_integration_setup.py`: Helper functions and configurations for N8N workflow setup

### Configuration Files
- `knowledge_base.json`: FAQ responses, product categories, and qualification questions
- `*_integration_config.json`: Platform-specific configuration for Crisp, Shopify, and N8N
- `enhanced_n8n_workflow.json`: Complete N8N workflow definition with nodes and connections

### Documentation
- `system_architecture.md`: High-level system design overview
- `SBDR Conversational Agent System - Complete Documentation.md`: Comprehensive project documentation
- `*_capabilities.md`: Platform-specific capability documentation

## Common Development Commands

### Testing
```bash
# Run all tests
python testing_framework.py

# Run specific test classes
python -m unittest testing_framework.SBDRAgentTestCase
python -m unittest testing_framework.IntegrationTest
```

### SBDR Agent Development
```bash
# Test the enhanced SBDR agent with sample conversations
python enhanced_sbdr_logic.py

# Test basic SBDR agent
python sbdr_agent_logic.py
```

### N8N Setup
```bash
# Generate N8N configuration files
python n8n_integration_setup.py
```

### JSON Validation
```bash
# Validate configuration files
python -m json.tool knowledge_base.json
python -m json.tool enhanced_n8n_workflow.json
```

## Key Architecture Patterns

### Intent Detection System
The system uses hybrid pattern matching combining:
- Rule-based regex patterns for common intents (greeting, product inquiry, pricing)
- Context-aware classification using conversation history
- Knowledge base integration for domain-specific responses

### Lead Qualification Framework
Multi-factor scoring algorithm evaluates:
- Budget indicators (explicit amounts, ranges, comparative statements)
- Product interest specificity (categories, brands, features)
- Use case alignment (business, gaming, education, creative)
- Timeline urgency (immediate, researching, specific timeframes)
- Engagement level (conversation depth, response quality)

### Conversation State Management
- Session-based user profiles with persistent conversation history
- Dynamic qualification status tracking (not_started → in_progress → qualified/unqualified)
- Context-aware question generation to fill qualification gaps
- Automated handoff triggers based on qualification score and conversation patterns

### N8N Workflow Design
- Webhook-driven message processing from Crisp
- Function nodes with embedded JavaScript for business logic
- Conditional routing based on intent detection and qualification status
- Integration with Shopify for real-time product information
- Automated handoff notifications for qualified leads

## Integration Points

### Crisp Integration
- Webhook processing for incoming messages from multiple channels
- Response delivery with message formatting per channel requirements
- Context preservation across conversation sessions

### Shopify Integration  
- Product catalog access with search and filtering
- Real-time inventory checking
- Customer profile and order history retrieval

### OpenAI Integration
- System prompt engineering for SBDR persona
- Dynamic context injection for personalized responses
- Response quality optimization through prompt tuning

## Testing Strategy

The testing framework covers:
- **Unit Tests**: Intent detection, qualification extraction, user profile management
- **Integration Tests**: Crisp webhooks, Shopify API calls, N8N workflow execution
- **End-to-End Tests**: Complete customer journey simulation from greeting to handoff
- **Performance Tests**: Concurrent session handling, response time validation

## Development Guidelines

### Configuration Management
- All API credentials stored in separate config files (not committed)
- Environment-specific settings isolated in dedicated configuration objects
- Knowledge base content managed as structured JSON for easy updates

### Error Handling
- Graceful degradation when external services are unavailable
- Fallback responses from knowledge base when AI services fail  
- Comprehensive logging and monitoring for production troubleshooting

### Conversation Quality
- Response appropriateness validation through automated content analysis
- Qualification question optimization based on conversation context
- Human agent handoff triggered by qualification completion or explicit requests