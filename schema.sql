-- MindEase AI Database Schema
-- Run this to create the database manually (optional, app will auto-create)

CREATE DATABASE IF NOT EXISTS mindease_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE mindease_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) DEFAULT '',
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes for performance
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Check-ins table
CREATE TABLE IF NOT EXISTS checkins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    sentiment VARCHAR(20) DEFAULT 'NEUTRAL',
    sentiment_score DECIMAL(3,2) DEFAULT 0.0,
    recommendation TEXT,
    question_index INT DEFAULT 0,
    question TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key relationship
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes for performance
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_sentiment (sentiment),
    INDEX idx_user_date (user_id, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sessions table (for persistent session management)
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL 24 HOUR),
    
    -- Foreign key relationship
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Wellness activities table
CREATE TABLE IF NOT EXISTS wellness_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    duration_minutes INT DEFAULT 5,
    instructions JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sample data for wellness activities
INSERT IGNORE INTO wellness_activities (title, description, category, duration_minutes, instructions) VALUES
('4-7-8 Breathing Exercise', 'A calming breathing technique to reduce stress instantly.', 'breathing', 3, 
 '["Sit comfortably with your back straight", "Exhale completely through your mouth", "Close your mouth and inhale through your nose for 4 counts", "Hold your breath for 7 counts", "Exhale through your mouth for 8 counts", "Repeat this cycle 3-4 times"]'),

('Quick Desk Stretches', 'Simple movements to release tension at your workspace.', 'movement', 5,
 '["Roll your shoulders backward 10 times", "Gentle neck side bends (hold for 10 seconds each side)", "Seated spinal twist (hold for 15 seconds each direction)", "Wrist and ankle circles (10 times each direction)", "Stand up and do 10 gentle toe touches"]'),

('Gratitude Moment', 'A mindfulness exercise to shift focus to positive aspects.', 'mindfulness', 2,
 '["Think of one person you are grateful for today", "Recall a recent positive experience, however small", "Notice something beautiful in your current environment", "Feel the warmth of gratitude in your heart", "Take three deep, appreciative breaths"]'),

('5-Minute Energy Boost', 'Quick exercises to increase energy when feeling tired.', 'energy', 5,
 '["Do 20 jumping jacks or march in place", "Take 10 deep breaths with arms raised overhead", "Do gentle neck and shoulder rolls", "Drink a glass of water mindfully", "Look out the window or at something distant for 1 minute"]'),

('Progressive Muscle Relaxation', 'Systematic technique to release physical tension.', 'relaxation', 10,
 '["Sit or lie down comfortably", "Tense and release your toes for 5 seconds", "Move up to calves, thighs, abdomen", "Continue with hands, arms, shoulders", "Finish with face and head muscles", "Take 5 deep breaths feeling completely relaxed"]');

-- Create a view for user wellness statistics
CREATE OR REPLACE VIEW user_wellness_stats AS
SELECT 
    u.id as user_id,
    u.username,
    COUNT(c.id) as total_checkins,
    AVG(c.sentiment_score) as avg_sentiment_score,
    COUNT(CASE WHEN c.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY) THEN 1 END) as weekly_checkins,
    COUNT(CASE WHEN c.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) THEN 1 END) as monthly_checkins,
    MAX(c.created_at) as last_checkin,
    (SELECT sentiment FROM checkins WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) as latest_sentiment
FROM users u
LEFT JOIN checkins c ON u.id = c.user_id
GROUP BY u.id, u.username;

-- Indexes for better performance
CREATE INDEX idx_checkins_user_sentiment ON checkins(user_id, sentiment);
CREATE INDEX idx_checkins_user_created ON checkins(user_id, created_at DESC);