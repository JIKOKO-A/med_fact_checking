-- PostgreSQL Database Initialization Script
-- This file uses PostgreSQL 16 syntax (not MSSQL)
-- Safe to ignore MSSQL linting errors
-- Used in docker-compose.yml for medical_factcheck database initialization

-- Initialize database schema
-- Enable trigram matching for full-text search on medical claims
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_claims_created_at ON claims(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_claims_verification_label ON claims(verification_label);
CREATE INDEX IF NOT EXISTS idx_claims_medical_domain ON claims(medical_domain);
CREATE INDEX IF NOT EXISTS idx_claims_user_id ON claims(user_id);

CREATE INDEX IF NOT EXISTS idx_logs_created_at ON verification_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_logs_claim_id ON verification_logs(claim_id);

CREATE INDEX IF NOT EXISTS idx_stats_date ON statistics(date);

-- Create materialized view for fast analytics
CREATE MATERIALIZED VIEW IF NOT EXISTS claim_stats_mv AS
SELECT 
    verification_label,
    medical_domain,
    COUNT(*) as count,
    AVG(confidence_score) as avg_confidence,
    DATE(created_at) as stat_date
FROM claims
GROUP BY verification_label, medical_domain, DATE(created_at);

CREATE INDEX IF NOT EXISTS idx_claim_stats_date ON claim_stats_mv(stat_date DESC);

-- Grant privileges
GRANT SELECT ON claim_stats_mv TO PUBLIC;
