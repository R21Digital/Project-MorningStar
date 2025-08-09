"""
Security Audit System Tables
Adds tamper-resistant audit logging tables with integrity protection
"""

VERSION = "004"
NAME = "security_audit_system" 
DESCRIPTION = "Create security audit logging tables with tamper protection"

# PostgreSQL version
UP_SQL_POSTGRES = """
-- Main security audit log table
CREATE TABLE IF NOT EXISTS security_audit_log (
    event_id UUID PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'authentication', 'authorization', 'data_access', 'data_modification',
        'system_access', 'configuration_change', 'security_violation', 
        'api_access', 'admin_action', 'error'
    )),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    outcome VARCHAR(20) NOT NULL CHECK (outcome IN ('success', 'failure', 'denied', 'error')),
    
    -- Timing and source
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    source_ip INET,
    user_agent TEXT,
    
    -- Actor identification
    user_id UUID REFERENCES users(id),
    username VARCHAR(255),
    session_id VARCHAR(255),
    api_key_id VARCHAR(16),
    
    -- Action details
    action TEXT NOT NULL,
    resource TEXT,
    resource_id TEXT,
    
    -- Event data
    details JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]',
    
    -- Risk assessment
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    threat_indicators JSONB DEFAULT '[]',
    
    -- Compliance
    compliance_tags JSONB DEFAULT '[]',
    data_classification VARCHAR(50) CHECK (data_classification IN (
        'public', 'internal', 'confidential', 'restricted', 'secret'
    )),
    
    -- Tamper protection
    event_hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64),
    signature TEXT NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit chain verification table
CREATE TABLE IF NOT EXISTS audit_chain_state (
    id SERIAL PRIMARY KEY,
    chain_name VARCHAR(100) UNIQUE NOT NULL,
    current_hash VARCHAR(64) NOT NULL,
    last_event_id UUID REFERENCES security_audit_log(event_id),
    event_count BIGINT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit configuration table
CREATE TABLE IF NOT EXISTS audit_configuration (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    enabled BOOLEAN DEFAULT true,
    min_severity VARCHAR(20) DEFAULT 'low',
    retention_days INTEGER DEFAULT 365,
    compliance_required JSONB DEFAULT '[]',
    risk_threshold INTEGER DEFAULT 50,
    notification_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON security_audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user ON security_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_type ON security_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_severity ON security_audit_log(severity);
CREATE INDEX IF NOT EXISTS idx_audit_outcome ON security_audit_log(outcome);
CREATE INDEX IF NOT EXISTS idx_audit_source_ip ON security_audit_log(source_ip);
CREATE INDEX IF NOT EXISTS idx_audit_risk_score ON security_audit_log(risk_score);
CREATE INDEX IF NOT EXISTS idx_audit_action ON security_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON security_audit_log(resource);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_audit_user_time ON security_audit_log(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_type_severity ON security_audit_log(event_type, severity);
CREATE INDEX IF NOT EXISTS idx_audit_ip_time ON security_audit_log(source_ip, timestamp);

-- JSON indexes for advanced querying
CREATE INDEX IF NOT EXISTS idx_audit_details_gin ON security_audit_log USING gin(details);
CREATE INDEX IF NOT EXISTS idx_audit_tags_gin ON security_audit_log USING gin(tags);
CREATE INDEX IF NOT EXISTS idx_audit_threat_indicators_gin ON security_audit_log USING gin(threat_indicators);
CREATE INDEX IF NOT EXISTS idx_audit_compliance_gin ON security_audit_log USING gin(compliance_tags);

-- Table comments for documentation
COMMENT ON TABLE security_audit_log IS 'Tamper-resistant security audit log with cryptographic integrity';
COMMENT ON TABLE audit_chain_state IS 'Maintains audit log chain integrity state';
COMMENT ON TABLE audit_configuration IS 'Audit system configuration and rules';

-- Column comments
COMMENT ON COLUMN security_audit_log.event_hash IS 'SHA-256 hash of event content';
COMMENT ON COLUMN security_audit_log.previous_hash IS 'Hash of previous event in chain';
COMMENT ON COLUMN security_audit_log.signature IS 'Cryptographic signature for tamper detection';
COMMENT ON COLUMN security_audit_log.risk_score IS 'Calculated risk score (0-100)';
COMMENT ON COLUMN security_audit_log.compliance_tags IS 'Compliance frameworks applicable to this event';

-- Default audit configuration entries
INSERT INTO audit_configuration (event_type, enabled, min_severity, retention_days, compliance_required) VALUES
('authentication', true, 'medium', 2555, '["SOC2", "PCI-DSS", "GDPR"]'),
('authorization', true, 'medium', 2555, '["SOC2", "GDPR"]'),
('data_access', true, 'low', 2555, '["GDPR", "HIPAA", "SOC2"]'),
('data_modification', true, 'medium', 2555, '["GDPR", "HIPAA", "SOX"]'),
('system_access', true, 'medium', 1095, '["SOC2"]'),
('configuration_change', true, 'high', 2555, '["SOC2", "PCI-DSS"]'),
('security_violation', true, 'critical', 2555, '["SOC2", "PCI-DSS", "GDPR"]'),
('api_access', true, 'low', 365, '["SOC2"]'),
('admin_action', true, 'high', 2555, '["SOC2", "SOX"]'),
('error', true, 'medium', 365, '["SOC2"]')
ON CONFLICT DO NOTHING;

-- Initialize audit chain state
INSERT INTO audit_chain_state (chain_name, current_hash, event_count) VALUES
('main_audit_chain', encode(sha256('MS11_AUDIT_CHAIN_GENESIS'::bytea), 'hex'), 0)
ON CONFLICT DO NOTHING;
"""

# SQLite version  
UP_SQL_SQLITE = """
-- Main security audit log table
CREATE TABLE IF NOT EXISTS security_audit_log (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'authentication', 'authorization', 'data_access', 'data_modification',
        'system_access', 'configuration_change', 'security_violation', 
        'api_access', 'admin_action', 'error'
    )),
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    outcome TEXT NOT NULL CHECK (outcome IN ('success', 'failure', 'denied', 'error')),
    
    -- Timing and source
    timestamp TEXT NOT NULL,
    source_ip TEXT,
    user_agent TEXT,
    
    -- Actor identification
    user_id TEXT REFERENCES users(id),
    username TEXT,
    session_id TEXT,
    api_key_id TEXT,
    
    -- Action details
    action TEXT NOT NULL,
    resource TEXT,
    resource_id TEXT,
    
    -- Event data
    details TEXT DEFAULT '{}',
    tags TEXT DEFAULT '[]',
    
    -- Risk assessment
    risk_score INTEGER CHECK (risk_score >= 0 AND risk_score <= 100),
    threat_indicators TEXT DEFAULT '[]',
    
    -- Compliance
    compliance_tags TEXT DEFAULT '[]',
    data_classification TEXT CHECK (data_classification IN (
        'public', 'internal', 'confidential', 'restricted', 'secret'
    )),
    
    -- Tamper protection
    event_hash TEXT NOT NULL,
    previous_hash TEXT,
    signature TEXT NOT NULL,
    
    -- Metadata
    created_at TEXT DEFAULT (datetime('now'))
);

-- Audit chain verification table
CREATE TABLE IF NOT EXISTS audit_chain_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT UNIQUE NOT NULL,
    current_hash TEXT NOT NULL,
    last_event_id TEXT REFERENCES security_audit_log(event_id),
    event_count INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Audit configuration table
CREATE TABLE IF NOT EXISTS audit_configuration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    min_severity TEXT DEFAULT 'low',
    retention_days INTEGER DEFAULT 365,
    compliance_required TEXT DEFAULT '[]',
    risk_threshold INTEGER DEFAULT 50,
    notification_enabled BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON security_audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_user ON security_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_type ON security_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_severity ON security_audit_log(severity);
CREATE INDEX IF NOT EXISTS idx_audit_outcome ON security_audit_log(outcome);
CREATE INDEX IF NOT EXISTS idx_audit_source_ip ON security_audit_log(source_ip);
CREATE INDEX IF NOT EXISTS idx_audit_risk_score ON security_audit_log(risk_score);
CREATE INDEX IF NOT EXISTS idx_audit_action ON security_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON security_audit_log(resource);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_audit_user_time ON security_audit_log(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_type_severity ON security_audit_log(event_type, severity);
CREATE INDEX IF NOT EXISTS idx_audit_ip_time ON security_audit_log(source_ip, timestamp);

-- Default audit configuration entries
INSERT OR IGNORE INTO audit_configuration (event_type, enabled, min_severity, retention_days, compliance_required) VALUES
('authentication', 1, 'medium', 2555, '["SOC2", "PCI-DSS", "GDPR"]'),
('authorization', 1, 'medium', 2555, '["SOC2", "GDPR"]'),
('data_access', 1, 'low', 2555, '["GDPR", "HIPAA", "SOC2"]'),
('data_modification', 1, 'medium', 2555, '["GDPR", "HIPAA", "SOX"]'),
('system_access', 1, 'medium', 1095, '["SOC2"]'),
('configuration_change', 1, 'high', 2555, '["SOC2", "PCI-DSS"]'),
('security_violation', 1, 'critical', 2555, '["SOC2", "PCI-DSS", "GDPR"]'),
('api_access', 1, 'low', 365, '["SOC2"]'),
('admin_action', 1, 'high', 2555, '["SOC2", "SOX"]'),
('error', 1, 'medium', 365, '["SOC2"]');

-- Initialize audit chain state  
INSERT OR IGNORE INTO audit_chain_state (chain_name, current_hash, event_count) VALUES
('main_audit_chain', '7d865e959b2466918c9863afca942d0fb89d7c9ac0c99bafc3749504ded97730', 0);

-- Triggers for updating timestamps
CREATE TRIGGER IF NOT EXISTS update_audit_config_timestamp 
AFTER UPDATE ON audit_configuration
FOR EACH ROW
BEGIN
    UPDATE audit_configuration SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_chain_state_timestamp
AFTER UPDATE ON audit_chain_state  
FOR EACH ROW
BEGIN
    UPDATE audit_chain_state SET updated_at = datetime('now') WHERE id = NEW.id;
END;
"""

# Rollback SQL
DOWN_SQL = """
-- Remove triggers
DROP TRIGGER IF EXISTS update_audit_config_timestamp;
DROP TRIGGER IF EXISTS update_chain_state_timestamp;

-- Remove indexes
DROP INDEX IF EXISTS idx_audit_timestamp;
DROP INDEX IF EXISTS idx_audit_user;
DROP INDEX IF EXISTS idx_audit_type;
DROP INDEX IF EXISTS idx_audit_severity;
DROP INDEX IF EXISTS idx_audit_outcome;
DROP INDEX IF EXISTS idx_audit_source_ip;
DROP INDEX IF EXISTS idx_audit_risk_score;
DROP INDEX IF EXISTS idx_audit_action;
DROP INDEX IF EXISTS idx_audit_resource;
DROP INDEX IF EXISTS idx_audit_user_time;
DROP INDEX IF EXISTS idx_audit_type_severity;
DROP INDEX IF EXISTS idx_audit_ip_time;
DROP INDEX IF EXISTS idx_audit_details_gin;
DROP INDEX IF EXISTS idx_audit_tags_gin;
DROP INDEX IF EXISTS idx_audit_threat_indicators_gin;
DROP INDEX IF EXISTS idx_audit_compliance_gin;

-- Remove tables
DROP TABLE IF EXISTS audit_configuration;
DROP TABLE IF EXISTS audit_chain_state;  
DROP TABLE IF EXISTS security_audit_log;
"""

# Set UP_SQL based on database type (will be determined at runtime)
UP_SQL = UP_SQL_POSTGRES  # Default, will be updated by migration system