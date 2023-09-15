CREATE TABLE IF NOT EXISTS t_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    description TEXT,
    valid_from DATETIME,
    valid_upto DATETIME
);