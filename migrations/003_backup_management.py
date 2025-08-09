"""
Backup Management Tables
Adds tables for tracking backup operations and metadata
"""

VERSION = "003"
NAME = "backup_management"
DESCRIPTION = "Add backup tracking and recovery management tables"

# PostgreSQL version
UP_SQL_POSTGRES = """
-- Backup operations table
CREATE TABLE IF NOT EXISTS backup_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_id VARCHAR(255) UNIQUE NOT NULL,
    backup_type VARCHAR(50) CHECK (backup_type IN ('full', 'incremental', 'differential', 'schema_only')),
    status VARCHAR(50) CHECK (status IN ('pending', 'running', 'completed', 'failed', 'corrupted')),
    database_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT DEFAULT 0,
    checksum VARCHAR(64),
    compressed BOOLEAN DEFAULT false,
    encrypted BOOLEAN DEFAULT false,
    tables_included TEXT[], -- Array of table names
    records_count BIGINT DEFAULT 0,
    schema_version VARCHAR(50),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- S3 storage info
    s3_bucket VARCHAR(255),
    s3_key TEXT,
    s3_uploaded BOOLEAN DEFAULT false,
    
    -- Dependencies for incremental backups
    parent_backup_id VARCHAR(255) REFERENCES backup_operations(backup_id),
    
    -- Metadata as JSON
    metadata JSONB DEFAULT '{}'
);

-- Backup restore operations table
CREATE TABLE IF NOT EXISTS restore_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    restore_id VARCHAR(255) UNIQUE NOT NULL,
    backup_id VARCHAR(255) REFERENCES backup_operations(backup_id),
    target_database VARCHAR(255),
    tables_restored TEXT[],
    records_restored BIGINT DEFAULT 0,
    status VARCHAR(50) CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    dry_run BOOLEAN DEFAULT false,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- User who initiated restore
    restored_by UUID REFERENCES users(id),
    
    -- Restore options as JSON
    restore_options JSONB DEFAULT '{}'
);

-- Backup schedules table
CREATE TABLE IF NOT EXISTS backup_schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    backup_type VARCHAR(50) CHECK (backup_type IN ('full', 'incremental', 'differential')),
    enabled BOOLEAN DEFAULT true,
    
    -- Schedule configuration
    interval_hours INTEGER NOT NULL,
    retention_days INTEGER DEFAULT 30,
    
    -- Tables to include
    tables_include TEXT[],
    tables_exclude TEXT[],
    
    -- Storage options
    compression BOOLEAN DEFAULT true,
    encryption BOOLEAN DEFAULT false,
    s3_upload BOOLEAN DEFAULT false,
    
    -- Last execution
    last_run TIMESTAMP WITH TIME ZONE,
    last_backup_id VARCHAR(255) REFERENCES backup_operations(backup_id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_backup_operations_type_status ON backup_operations(backup_type, status);
CREATE INDEX IF NOT EXISTS idx_backup_operations_created_at ON backup_operations(created_at);
CREATE INDEX IF NOT EXISTS idx_backup_operations_backup_id ON backup_operations(backup_id);
CREATE INDEX IF NOT EXISTS idx_backup_operations_parent ON backup_operations(parent_backup_id);

CREATE INDEX IF NOT EXISTS idx_restore_operations_backup_id ON restore_operations(backup_id);
CREATE INDEX IF NOT EXISTS idx_restore_operations_status ON restore_operations(status);
CREATE INDEX IF NOT EXISTS idx_restore_operations_created_at ON restore_operations(created_at);

CREATE INDEX IF NOT EXISTS idx_backup_schedules_enabled ON backup_schedules(enabled);
CREATE INDEX IF NOT EXISTS idx_backup_schedules_last_run ON backup_schedules(last_run);

-- Add table comments
COMMENT ON TABLE backup_operations IS 'Database backup operations tracking';
COMMENT ON TABLE restore_operations IS 'Database restore operations tracking';
COMMENT ON TABLE backup_schedules IS 'Automated backup schedule configuration';

-- Column comments
COMMENT ON COLUMN backup_operations.backup_id IS 'Unique backup identifier';
COMMENT ON COLUMN backup_operations.tables_included IS 'Array of table names included in backup';
COMMENT ON COLUMN backup_operations.parent_backup_id IS 'Parent backup for incremental backups';
COMMENT ON COLUMN restore_operations.dry_run IS 'Whether this was a dry run restore';
COMMENT ON COLUMN backup_schedules.tables_include IS 'Tables to include in scheduled backups';
COMMENT ON COLUMN backup_schedules.tables_exclude IS 'Tables to exclude from scheduled backups';
"""

# SQLite version  
UP_SQL_SQLITE = """
-- Backup operations table
CREATE TABLE IF NOT EXISTS backup_operations (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('ab89',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    backup_id TEXT UNIQUE NOT NULL,
    backup_type TEXT CHECK (backup_type IN ('full', 'incremental', 'differential', 'schema_only')),
    status TEXT CHECK (status IN ('pending', 'running', 'completed', 'failed', 'corrupted')),
    database_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    checksum TEXT,
    compressed BOOLEAN DEFAULT 0,
    encrypted BOOLEAN DEFAULT 0,
    tables_included TEXT, -- JSON array of table names
    records_count INTEGER DEFAULT 0,
    schema_version TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- S3 storage info
    s3_bucket TEXT,
    s3_key TEXT,
    s3_uploaded BOOLEAN DEFAULT 0,
    
    -- Dependencies for incremental backups
    parent_backup_id TEXT REFERENCES backup_operations(backup_id),
    
    -- Metadata as JSON
    metadata TEXT DEFAULT '{}'
);

-- Backup restore operations table
CREATE TABLE IF NOT EXISTS restore_operations (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('ab89',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    restore_id TEXT UNIQUE NOT NULL,
    backup_id TEXT REFERENCES backup_operations(backup_id),
    target_database TEXT,
    tables_restored TEXT, -- JSON array
    records_restored INTEGER DEFAULT 0,
    status TEXT CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    dry_run BOOLEAN DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- User who initiated restore
    restored_by TEXT REFERENCES users(id),
    
    -- Restore options as JSON
    restore_options TEXT DEFAULT '{}'
);

-- Backup schedules table
CREATE TABLE IF NOT EXISTS backup_schedules (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('ab89',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    name TEXT UNIQUE NOT NULL,
    backup_type TEXT CHECK (backup_type IN ('full', 'incremental', 'differential')),
    enabled BOOLEAN DEFAULT 1,
    
    -- Schedule configuration
    interval_hours INTEGER NOT NULL,
    retention_days INTEGER DEFAULT 30,
    
    -- Tables to include
    tables_include TEXT, -- JSON array
    tables_exclude TEXT, -- JSON array
    
    -- Storage options
    compression BOOLEAN DEFAULT 1,
    encryption BOOLEAN DEFAULT 0,
    s3_upload BOOLEAN DEFAULT 0,
    
    -- Last execution
    last_run TIMESTAMP,
    last_backup_id TEXT REFERENCES backup_operations(backup_id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_backup_operations_type_status ON backup_operations(backup_type, status);
CREATE INDEX IF NOT EXISTS idx_backup_operations_created_at ON backup_operations(created_at);
CREATE INDEX IF NOT EXISTS idx_backup_operations_backup_id ON backup_operations(backup_id);
CREATE INDEX IF NOT EXISTS idx_backup_operations_parent ON backup_operations(parent_backup_id);

CREATE INDEX IF NOT EXISTS idx_restore_operations_backup_id ON restore_operations(backup_id);
CREATE INDEX IF NOT EXISTS idx_restore_operations_status ON restore_operations(status);
CREATE INDEX IF NOT EXISTS idx_restore_operations_created_at ON restore_operations(created_at);

CREATE INDEX IF NOT EXISTS idx_backup_schedules_enabled ON backup_schedules(enabled);
CREATE INDEX IF NOT EXISTS idx_backup_schedules_last_run ON backup_schedules(last_run);

-- Create triggers for updated_at (SQLite)
CREATE TRIGGER IF NOT EXISTS update_backup_schedules_updated_at
    AFTER UPDATE ON backup_schedules
    FOR EACH ROW
    BEGIN
        UPDATE backup_schedules SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;
"""

# Rollback SQL
DOWN_SQL = """
DROP TRIGGER IF EXISTS update_backup_schedules_updated_at;

DROP INDEX IF EXISTS idx_backup_operations_type_status;
DROP INDEX IF EXISTS idx_backup_operations_created_at;
DROP INDEX IF EXISTS idx_backup_operations_backup_id;
DROP INDEX IF EXISTS idx_backup_operations_parent;
DROP INDEX IF EXISTS idx_restore_operations_backup_id;
DROP INDEX IF EXISTS idx_restore_operations_status;
DROP INDEX IF EXISTS idx_restore_operations_created_at;
DROP INDEX IF EXISTS idx_backup_schedules_enabled;
DROP INDEX IF EXISTS idx_backup_schedules_last_run;

DROP TABLE IF EXISTS restore_operations;
DROP TABLE IF EXISTS backup_schedules;
DROP TABLE IF EXISTS backup_operations;
"""

# Set UP_SQL based on database type (will be determined at runtime)
UP_SQL = UP_SQL_POSTGRES  # Default, will be updated by migration system