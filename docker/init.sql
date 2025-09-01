-- Multi-Agent SBDR System Database Initialization
-- This script creates the necessary tables for conversation tracking and analytics

-- Create database schema
CREATE SCHEMA IF NOT EXISTS sbdr;

-- Set search path
SET search_path = sbdr, public;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) DEFAULT 'Guest',
    email VARCHAR(255),
    customer_tier VARCHAR(50) DEFAULT 'prospect',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) REFERENCES users(session_id) ON DELETE CASCADE,
    budget VARCHAR(50),
    product_interest VARCHAR(255),
    use_case VARCHAR(255),
    timeline VARCHAR(255),
    qualification_status VARCHAR(50) DEFAULT 'not_started',
    engagement_score INTEGER DEFAULT 0,
    current_agent VARCHAR(50),
    lifetime_value DECIMAL(10,2) DEFAULT 0.00,
    last_interaction TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) REFERENCES users(session_id) ON DELETE CASCADE,
    message_id VARCHAR(255),
    content TEXT NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    sender VARCHAR(255) NOT NULL,
    intent VARCHAR(100),
    agent_type VARCHAR(50),
    confidence DECIMAL(3,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create agent interactions table
CREATE TABLE IF NOT EXISTS agent_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) REFERENCES users(session_id) ON DELETE CASCADE,
    from_agent VARCHAR(50),
    to_agent VARCHAR(50),
    handoff_reason VARCHAR(255),
    handoff_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create system metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    tags JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create conversation analytics table
CREATE TABLE IF NOT EXISTS conversation_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) REFERENCES users(session_id) ON DELETE CASCADE,
    total_messages INTEGER DEFAULT 0,
    total_agents INTEGER DEFAULT 0,
    qualification_progression JSONB,
    intents_detected JSONB,
    agents_involved JSONB,
    handoff_count INTEGER DEFAULT 0,
    session_duration INTEGER DEFAULT 0,
    final_qualification_status VARCHAR(50),
    business_value DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_session_id ON users(session_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_session_id ON user_profiles(session_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_qualification ON user_profiles(qualification_status);
CREATE INDEX IF NOT EXISTS idx_user_profiles_customer_tier ON user_profiles(customer_tier);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_agent_type ON conversations(agent_type);
CREATE INDEX IF NOT EXISTS idx_conversations_intent ON conversations(intent);
CREATE INDEX IF NOT EXISTS idx_agent_interactions_session_id ON agent_interactions(session_id);
CREATE INDEX IF NOT EXISTS idx_system_metrics_name ON system_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_metrics_recorded_at ON system_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_conversation_analytics_session_id ON conversation_analytics(session_id);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic timestamp updates
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_analytics_updated_at BEFORE UPDATE ON conversation_analytics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO users (session_id, name, email, customer_tier) VALUES
    ('demo_session_1', 'Demo User 1', 'demo1@example.com', 'prospect'),
    ('demo_session_2', 'Demo Customer', 'customer@example.com', 'customer'),
    ('demo_session_3', 'VIP Client', 'vip@example.com', 'vip')
ON CONFLICT (session_id) DO NOTHING;

INSERT INTO user_profiles (session_id, budget, product_interest, use_case, qualification_status, engagement_score) VALUES
    ('demo_session_1', '1500', 'laptops', 'business', 'in_progress', 3),
    ('demo_session_2', '2000', 'workstations', 'design', 'qualified', 5),
    ('demo_session_3', '5000', 'enterprise', 'corporate', 'qualified', 8)
ON CONFLICT (session_id) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW conversation_summary AS
SELECT 
    u.session_id,
    u.name,
    u.email,
    u.customer_tier,
    up.qualification_status,
    up.engagement_score,
    up.current_agent,
    COUNT(c.id) as message_count,
    MAX(c.created_at) as last_message_at,
    COUNT(DISTINCT c.agent_type) as agents_used
FROM users u
LEFT JOIN user_profiles up ON u.session_id = up.session_id
LEFT JOIN conversations c ON u.session_id = c.session_id
GROUP BY u.session_id, u.name, u.email, u.customer_tier, 
         up.qualification_status, up.engagement_score, up.current_agent;

CREATE OR REPLACE VIEW agent_performance AS
SELECT 
    c.agent_type,
    COUNT(*) as total_interactions,
    COUNT(DISTINCT c.session_id) as unique_sessions,
    AVG(c.confidence) as avg_confidence,
    COUNT(CASE WHEN up.qualification_status = 'qualified' THEN 1 END) as qualified_leads
FROM conversations c
LEFT JOIN user_profiles up ON c.session_id = up.session_id
WHERE c.agent_type IS NOT NULL
GROUP BY c.agent_type;

CREATE OR REPLACE VIEW daily_metrics AS
SELECT 
    DATE(c.created_at) as date,
    COUNT(*) as total_messages,
    COUNT(DISTINCT c.session_id) as unique_sessions,
    COUNT(DISTINCT c.agent_type) as agents_used,
    AVG(up.engagement_score) as avg_engagement
FROM conversations c
LEFT JOIN user_profiles up ON c.session_id = up.session_id
GROUP BY DATE(c.created_at)
ORDER BY date DESC;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA sbdr TO sbdr_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sbdr TO sbdr_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sbdr TO sbdr_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA sbdr TO sbdr_user;

-- Create additional user for read-only access (analytics/reporting)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'sbdr_reader') THEN
        CREATE ROLE sbdr_reader WITH LOGIN PASSWORD 'sbdr_read_pass';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE sbdr_db TO sbdr_reader;
GRANT USAGE ON SCHEMA sbdr TO sbdr_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA sbdr TO sbdr_reader;

COMMIT;