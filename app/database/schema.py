def create_all_tables(conn):
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT
        )
    """)

    # User token table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_tokens (
            user_id TEXT PRIMARY KEY,
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TEXT,
            token_type TEXT,
            scope TEXT
        )
    """)

    # Email logs table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            gmail_msg_id TEXT,
            from_email TEXT,
            subject TEXT,
            body TEXT,
            category TEXT,
            suggested_reply TEXT,
            status TEXT,
            created_at TEXT,
            sent_at TEXT
        )
    """)

    conn.commit()
