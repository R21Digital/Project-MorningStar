-- MS11 PostgreSQL Initialization Script
-- This script runs when the PostgreSQL container is first created

-- Create additional databases for development and testing
SELECT 'CREATE DATABASE ms11_dev' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ms11_dev')\gexec
SELECT 'CREATE DATABASE ms11_test' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ms11_test')\gexec

-- Create database extensions that might be useful
\c ms11
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c ms11_dev
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c ms11_test
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Switch back to main database
\c ms11

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE ms11 TO ms11;
GRANT ALL PRIVILEGES ON DATABASE ms11_dev TO ms11;
GRANT ALL PRIVILEGES ON DATABASE ms11_test TO ms11;