"""
Performance Optimization Indexes
Adds specialized indexes for query performance optimization
"""

VERSION = "002"
NAME = "performance_indexes"
DESCRIPTION = "Add performance optimization indexes and constraints"

UP_SQL = """
-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_sessions_user_status ON sessions(user_id, status);
CREATE INDEX IF NOT EXISTS idx_sessions_character_server ON sessions(character_name, server_name);
CREATE INDEX IF NOT EXISTS idx_commands_session_status ON commands(session_id, status);
CREATE INDEX IF NOT EXISTS idx_commands_type_status ON commands(command_type, status);
CREATE INDEX IF NOT EXISTS idx_metrics_session_name ON metrics(session_id, metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON metrics(metric_name, collected_at);
CREATE INDEX IF NOT EXISTS idx_alerts_type_level ON alerts(alert_type, level);
CREATE INDEX IF NOT EXISTS idx_audit_user_action ON audit_logs(user_id, action);

-- Partial indexes for active records (PostgreSQL specific, will be ignored in SQLite)
CREATE INDEX IF NOT EXISTS idx_active_sessions ON sessions(user_id, created_at) WHERE status IN ('running', 'paused');
CREATE INDEX IF NOT EXISTS idx_unresolved_alerts ON alerts(level, created_at) WHERE resolved = false;
CREATE INDEX IF NOT EXISTS idx_recent_commands ON commands(session_id, created_at) WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours';

-- Expression indexes for JSON fields (PostgreSQL)
CREATE INDEX IF NOT EXISTS idx_user_role ON users((preferences->>'theme')) WHERE preferences IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_session_config ON sessions((config->>'auto_pause')) WHERE config IS NOT NULL;

-- Add database constraints for data integrity
ALTER TABLE users ADD CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 255);
ALTER TABLE users ADD CONSTRAINT chk_email_format CHECK (email IS NULL OR email LIKE '%@%.%');
ALTER TABLE sessions ADD CONSTRAINT chk_character_name_length CHECK (LENGTH(character_name) >= 1 AND LENGTH(character_name) <= 255);
ALTER TABLE commands ADD CONSTRAINT chk_command_text_not_empty CHECK (LENGTH(TRIM(command_text)) > 0);

-- Add table comments for documentation (PostgreSQL)
COMMENT ON TABLE users IS 'User accounts and authentication information';
COMMENT ON TABLE sessions IS 'Gaming automation sessions';
COMMENT ON TABLE commands IS 'Commands executed during sessions';
COMMENT ON TABLE metrics IS 'Performance and usage metrics';
COMMENT ON TABLE alerts IS 'System alerts and notifications';
COMMENT ON TABLE plugins IS 'Installed plugins configuration';
COMMENT ON TABLE audit_logs IS 'Security and action audit trail';

-- Column comments
COMMENT ON COLUMN users.preferences IS 'User preferences stored as JSON';
COMMENT ON COLUMN sessions.config IS 'Session configuration parameters';
COMMENT ON COLUMN sessions.stats IS 'Session statistics and performance data';
COMMENT ON COLUMN commands.parameters IS 'Command execution parameters';
COMMENT ON COLUMN commands.result IS 'Command execution results and output';
COMMENT ON COLUMN metrics.metadata IS 'Additional metric context and tags';
COMMENT ON COLUMN alerts.data IS 'Alert-specific data and context';
"""

DOWN_SQL = """
-- Remove constraints
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_username_length;
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_email_format;  
ALTER TABLE sessions DROP CONSTRAINT IF EXISTS chk_character_name_length;
ALTER TABLE commands DROP CONSTRAINT IF EXISTS chk_command_text_not_empty;

-- Remove indexes
DROP INDEX IF EXISTS idx_sessions_user_status;
DROP INDEX IF EXISTS idx_sessions_character_server;
DROP INDEX IF EXISTS idx_commands_session_status;
DROP INDEX IF EXISTS idx_commands_type_status;
DROP INDEX IF EXISTS idx_metrics_session_name;
DROP INDEX IF EXISTS idx_metrics_name_time;
DROP INDEX IF EXISTS idx_alerts_type_level;
DROP INDEX IF EXISTS idx_audit_user_action;
DROP INDEX IF EXISTS idx_active_sessions;
DROP INDEX IF EXISTS idx_unresolved_alerts;
DROP INDEX IF EXISTS idx_recent_commands;
DROP INDEX IF EXISTS idx_user_role;
DROP INDEX IF EXISTS idx_session_config;
"""