\c autoshift_db;

CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL
);

CREATE TABLE employees (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    employee_id SERIAL PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    min_work_hours INT,
    max_work_hours INT
);

CREATE TABLE shifts (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    shift_id SERIAL PRIMARY KEY,
    shift_name VARCHAR(100) NOT NULL,
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

CREATE TABLE settings (
    account_id INT NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    dark_theme_enabled BOOLEAN NOT NULL,
    min_max_work_hours_enabled BOOLEAN NOT NULL,
    multi_emps_in_shift_enabled BOOLEAN NOT NULL,
    multi_shifts_one_emp_enabled BOOLEAN NOT NULL
);