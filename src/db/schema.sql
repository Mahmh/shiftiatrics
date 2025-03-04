\c shiftiatrics_db;

-- Types
CREATE TYPE weekend_days_enum AS ENUM ('Saturday & Sunday', 'Friday & Saturday', 'Sunday & Monday');
CREATE TYPE interval_enum AS ENUM ('Daily', 'Weekly', 'Monthly');

-- Tables
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    email VARCHAR(256) UNIQUE NOT NULL,
    hashed_password VARCHAR(128), -- Null for OAuth users
    oauth_provider VARCHAR(16),
    oauth_token VARCHAR(2048),
    oauth_id VARCHAR(64) UNIQUE,
    oauth_email VARCHAR(256) UNIQUE -- Email can change, but OAuth email cannot
);

CREATE TABLE tokens (
    account_id INT PRIMARY KEY REFERENCES accounts(account_id) ON DELETE CASCADE,
    token VARCHAR(256) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE TABLE employees (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    employee_id SERIAL PRIMARY KEY,
    employee_name VARCHAR(40) NOT NULL,
    min_work_hours INT,
    max_work_hours INT
);

CREATE TABLE shifts (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    shift_id SERIAL PRIMARY KEY,
    shift_name VARCHAR(40) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

CREATE TABLE schedules (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    schedule_id SERIAL PRIMARY KEY,
    schedule JSONB NOT NULL,  -- Array (month) of arrays (days) of arrays (shifts) of employee IDs
    month INT NOT NULL,
    year INT NOT NULL
);

CREATE TABLE holidays (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    holiday_id SERIAL PRIMARY KEY,
    holiday_name VARCHAR(40) NOT NULL,
    assigned_to INT[] NOT NULL,  -- Array of employee IDs
    start_date DATE NOT NULL,
    end_date DATE NOT NULL
);

CREATE TABLE settings (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    dark_theme_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    min_max_work_hours_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    multi_emps_in_shift_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    multi_shifts_one_emp_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    weekend_days weekend_days_enum NOT NULL DEFAULT 'Saturday & Sunday',
    max_emps_in_shift INT NOT NULL DEFAULT 1,
    email_ntf_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    email_ntf_interval interval_enum NOT NULL DEFAULT 'Monthly'
);