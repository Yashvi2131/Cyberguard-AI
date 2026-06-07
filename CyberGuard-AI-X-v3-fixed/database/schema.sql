-- CyberGuard AI X Database Schema
-- Database: cyberguard_ai
-- Run this in XAMPP phpMyAdmin or MySQL CLI

CREATE DATABASE IF NOT EXISTS cyberguard_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cyberguard_ai;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    complaint_text TEXT NOT NULL,
    language VARCHAR(20) DEFAULT 'en',
    translated_text TEXT,
    category VARCHAR(50),
    confidence_score FLOAT DEFAULT 0.0,
    severity ENUM('Low', 'Medium', 'High') DEFAULT 'Low',
    department VARCHAR(100),
    status ENUM('Pending', 'Under Review', 'Resolved', 'Closed') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_category (category),
    INDEX idx_severity (severity),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- Analytics Table
CREATE TABLE IF NOT EXISTS analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_category (category)
);

-- Severity Logs Table
CREATE TABLE IF NOT EXISTS severity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    severity_level ENUM('Low', 'Medium', 'High') NOT NULL,
    keywords_detected TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    INDEX idx_complaint_id (complaint_id),
    INDEX idx_severity_level (severity_level)
);

-- Login Logs Table
CREATE TABLE IF NOT EXISTS login_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_login_time (login_time)
);

-- Seed analytics categories
INSERT INTO analytics (category, count) VALUES
('Phishing', 0), ('Hacking', 0), ('Malware', 0),
('Online Fraud', 0), ('Financial Fraud', 0),
('Identity Theft', 0), ('Cyberbullying', 0)
ON DUPLICATE KEY UPDATE category = category;

-- Seed default admin user (password: Admin@123 - bcrypt hashed)
-- Run backend/seed_admin.py to insert with proper hashing
