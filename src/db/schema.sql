\c autoshift_db;

CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE employees (
    account_id INT NOT NULL REFERENCES accounts(account_id),
    employee_id SERIAL PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL
);

CREATE TABLE shifts (
    account_id INT NOT NULL REFERENCES accounts(account_id),
    shift_id SERIAL PRIMARY KEY,
    shift_name VARCHAR(100) NOT NULL,
    time_range VARCHAR(50) NOT NULL
);

CREATE TABLE schedules (
    account_id INT NOT NULL REFERENCES accounts(account_id),
    schedule_id SERIAL PRIMARY KEY,
    schedule TEXT NOT NULL
);

-- CREATE TABLE Settings (
--     account_id INT NOT NULL REFERENCES Accounts(account_id),
--     setting_id SERIAL PRIMARY KEY,
--     setting_name VARCHAR(100) NOT NULL,
--     setting_value TEXT NOT NULL,
-- );