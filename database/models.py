from __future__ import annotations

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS masters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    master_code TEXT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    professions TEXT NOT NULL DEFAULT '[]',
    birth_date TEXT,
    work_start_month INTEGER,
    work_start_year INTEGER,
    work_experience_text TEXT,
    phone TEXT NOT NULL,
    work_address TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    birth_date TEXT,
    created_by TEXT NOT NULL,
    is_registered INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    no_show_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS client_masters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    master_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(client_id, master_id),
    FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    duration_minutes INTEGER NOT NULL,
    price REAL NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    service_id INTEGER,
    appointment_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    price_amount REAL,
    status TEXT NOT NULL,
    created_by TEXT NOT NULL,
    is_confirmed_by_client INTEGER NOT NULL DEFAULT 0,
    cancelled_by TEXT,
    no_show_status TEXT NOT NULL DEFAULT 'pending',
    included_in_stats INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE,
    FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY(service_id) REFERENCES services(id)
);

CREATE TABLE IF NOT EXISTS free_windows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER NOT NULL,
    window_date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS waitlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    mode TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE,
    FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS waitlist_dates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waitlist_id INTEGER NOT NULL,
    selected_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(waitlist_id) REFERENCES waitlist(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS booking_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER UNIQUE NOT NULL,
    time_step_minutes INTEGER NOT NULL DEFAULT 30,
    first_booking_time TEXT NOT NULL DEFAULT '10:00',
    last_booking_time TEXT NOT NULL DEFAULT '19:00',
    booking_range_days INTEGER NOT NULL DEFAULT 14,
    manual_duration_options TEXT NOT NULL DEFAULT '[30,60,90,120,150,180,210,240]',
    client_booking_limit_type TEXT,
    client_booking_limit_value INTEGER,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS notifications_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER,
    client_id INTEGER,
    appointment_id INTEGER,
    notification_type TEXT NOT NULL,
    receiver_role TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    status TEXT NOT NULL,
    error_text TEXT,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE,
    FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY(appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER NOT NULL,
    stats_date TEXT NOT NULL,
    income_amount REAL NOT NULL DEFAULT 0,
    appointments_count INTEGER NOT NULL DEFAULT 0,
    worked_minutes INTEGER NOT NULL DEFAULT 0,
    cancelled_by_master_count INTEGER NOT NULL DEFAULT 0,
    cancelled_by_client_count INTEGER NOT NULL DEFAULT 0,
    no_show_count INTEGER NOT NULL DEFAULT 0,
    sleeping_clients_count INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS birthdays_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    master_id INTEGER NOT NULL,
    client_id INTEGER NOT NULL,
    birth_day TEXT NOT NULL,
    notified_year INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(master_id) REFERENCES masters(id) ON DELETE CASCADE,
    FOREIGN KEY(client_id) REFERENCES clients(id) ON DELETE CASCADE
);
"""
