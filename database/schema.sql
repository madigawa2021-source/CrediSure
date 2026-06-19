-- CrediSure Database Schema
-- This file contains MySQL CREATE TABLE statements for all CrediSure tables

-- Users table: Stores user account information
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- KYC Records table: Stores user Know Your Customer verification data
CREATE TABLE IF NOT EXISTS kyc_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    bvn VARCHAR(20),
    nin VARCHAR(20),
    address TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    verified_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Businesses table: Stores user business information
CREATE TABLE IF NOT EXISTS businesses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    business_name VARCHAR(255) NOT NULL,
    rc_number VARCHAR(50),
    industry VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Credit Assessments table: Stores credit score assessment results
CREATE TABLE IF NOT EXISTS credit_assessments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    monthly_income DECIMAL(15,2),
    monthly_expense DECIMAL(15,2),
    existing_loans DECIMAL(15,2),
    credit_score INT,
    rating VARCHAR(10),
    risk_level VARCHAR(20),
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Uploaded Documents table: Stores metadata for files uploaded by users
CREATE TABLE IF NOT EXISTS uploaded_documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    s3_key VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Loan Applications table: Stores user loan application data
CREATE TABLE IF NOT EXISTS loan_applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    assessment_id INT,
    amount_requested DECIMAL(15,2) NOT NULL,
    purpose TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (assessment_id) REFERENCES credit_assessments(id) ON DELETE CASCADE
);
