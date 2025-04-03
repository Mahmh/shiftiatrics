\c shiftiatrics_db;

-- Types
CREATE TYPE weekend_days_enum AS ENUM ('Saturday & Sunday', 'Friday & Saturday', 'Sunday & Monday');
CREATE TYPE token_type_enum AS ENUM ('auth', 'reset', 'verify');
CREATE TYPE pricing_plan_enum AS ENUM ('starter', 'growth', 'advanced', 'enterprise');

-- Tables
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    email VARCHAR(256) UNIQUE NOT NULL,
    hashed_password VARCHAR(128) NOT NULL,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    stripe_customer_id VARCHAR(128) UNIQUE NULL
);

CREATE TABLE tokens (
    token_id SERIAL PRIMARY KEY,
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    token VARCHAR(64) UNIQUE NOT NULL,
    token_type token_type_enum NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    plan pricing_plan_enum NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    stripe_subscription_id VARCHAR(128) UNIQUE NOT NULL
);

CREATE TABLE employees (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    employee_id SERIAL PRIMARY KEY,
    employee_name VARCHAR(40) NOT NULL,
    min_work_hours INT NOT NULL,
    max_work_hours INT NOT NULL
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
    month INT NOT NULL,  -- [0-11]
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
    account_id INT PRIMARY KEY REFERENCES accounts(account_id) ON DELETE CASCADE,
    dark_theme_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    weekend_days weekend_days_enum NOT NULL DEFAULT 'Saturday & Sunday'
);