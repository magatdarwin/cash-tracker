CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY NOT NULL,
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS owners (
    id INTEGER PRIMARY KEY NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS banks (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    account_number TEXT,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    maintain REAL NOT NULL DEFAULT 0,
    user_id INTEGER NOT NULL,
    bank_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (bank_id) REFERENCES banks (id),
    FOREIGN KEY (owner_id) REFERENCES owners (id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    target TEXT,
    account_id INTEGER NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts (id)
);