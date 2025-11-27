USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,     -- The Gmail address (unique)
    name TEXT,
    created_at TEXT,
    role TEXT
);
"""

USER_TOKENS_TABLE = """
CREATE TABLE IF NOT EXISTS user_tokens (
    user_id TEXT PRIMARY KEY,
    access_token TEXT,
    refresh_token TEXT,
    token_expiry TEXT,
    token_type TEXT,
    scope TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

EMAIL_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS email_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,                 -- NEW: link the log to a specific user
    gmail_msg_id TEXT,
    from_email TEXT,
    subject TEXT,
    body TEXT,
    category TEXT,
    suggested_reply TEXT,
    status TEXT,
    created_at TEXT,
    sent_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

def create_all_tables(conn):
    cursor = conn.cursor()
    cursor.execute(USERS_TABLE)
    cursor.execute(USER_TOKENS_TABLE)
    cursor.execute(EMAIL_LOGS_TABLE)
    conn.commit()
