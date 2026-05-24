-- ACD-SDI MySQL Schema

CREATE DATABASE IF NOT EXISTS acd_sdi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE acd_sdi;

-- Phase 5/7: Assets for Enrichment & Taint-Aware Scoring
CREATE TABLE IF NOT EXISTS assets (
    username VARCHAR(255) PRIMARY KEY,
    criticality ENUM('CRITICAL','HIGH','MEDIUM','LOW') DEFAULT 'LOW',
    mfa_status TINYINT(1) DEFAULT 0,
    privilege_level VARCHAR(50),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed basic assets for testing
INSERT IGNORE INTO assets (username, criticality, mfa_status, privilege_level, department) VALUES 
('admin','CRITICAL',0,'root','IT'),
('guest','LOW',0,'none','Demo'),
('root','CRITICAL',1,'superuser','System');

-- Phase 1 & 2: Raw Logs and Templates
CREATE TABLE IF NOT EXISTS raw_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    source_system VARCHAR(100),
    raw_message TEXT,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS parsed_templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT,
    template_string TEXT,
    source_system VARCHAR(100),
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Phase 8: Final Security Signals
CREATE TABLE IF NOT EXISTS security_signals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attack_type VARCHAR(255),
    anomaly_score ENUM('HIGH','MEDIUM','LOW','INFO'),
    confidence DECIMAL(5,2),
    risk_level ENUM('CRITICAL','HIGH','MEDIUM','LOW'),
    mitre_id VARCHAR(50),
    source_ip VARCHAR(50),
    target_user VARCHAR(255),
    event_count INT,
    reasoning TEXT,
    context_json JSON,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Phase 9: Incident Memory Store
CREATE TABLE IF NOT EXISTS incident_memory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type ENUM('ACTOR', 'TARGET', 'ACTION'),
    entity_value VARCHAR(255),
    incident_data JSON,
    feedback_score INT DEFAULT 0,
    analyst_notes TEXT,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY idx_entity (entity_type, entity_value)
);

-- Step 6: Narrative Engine
CREATE TABLE IF NOT EXISTS attack_storylines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    mitre_techniques JSON,
    involved_ips JSON,
    involved_users JSON,
    severity ENUM('CRITICAL', 'HIGH', 'MEDIUM', 'LOW'),
    storyline_markdown TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Phase 9: Statistical Anomaly Detection
CREATE TABLE IF NOT EXISTS daily_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL,
    entity_type ENUM('USER', 'IP') NOT NULL,
    entity_val VARCHAR(255) NOT NULL,
    event_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_stat (date, entity_type, entity_val)
);

CREATE TABLE IF NOT EXISTS user_baselines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    entity_type ENUM('USER', 'IP') NOT NULL,
    entity_val VARCHAR(255) NOT NULL,
    avg_events_per_day FLOAT DEFAULT 0.0,
    std_dev_events FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_baseline (entity_type, entity_val)
);
