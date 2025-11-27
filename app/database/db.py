import sqlite3
from config.settings import DB_FILE
from app.database.schema import create_all_tables


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    create_all_tables(conn)
    conn.close()
def add_user(user_id, name, role="user"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO users (id, name, role, created_at) VALUES (?, ?, ?, datetime('now'))",
        (user_id, name, role)
    )
    conn.commit()
    conn.close()


def save_user_tokens(user_id, access, refresh, expiry, token_type, scope):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO user_tokens 
        (user_id, access_token, refresh_token, token_expiry, token_type, scope)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, access, refresh, expiry, token_type, scope)
    )
    conn.commit()
    conn.close()


def get_user_tokens(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_tokens WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row
def get_pending_emails_for_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM email_logs
        WHERE user_id = ? AND status = 'pending'
        ORDER BY created_at ASC
        """,
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

