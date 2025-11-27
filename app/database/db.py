import sqlite3
import os
from app.config.config import DB_FILE
from app.database.schema import create_all_tables


# -----------------------------------
# DB Connection
# -----------------------------------
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    create_all_tables(conn)
    conn.close()


# -----------------------------------
# EMAIL LOGS
# -----------------------------------
def log_email(user_id, gmail_msg_id, from_email, subject, body, category, suggested_reply, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO email_logs 
        (user_id, gmail_msg_id, from_email, subject, body, category, suggested_reply, status, created_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (user_id, gmail_msg_id, from_email, subject, body, category, suggested_reply, status)
    )
    conn.commit()
    conn.close()


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


def get_email_log_by_id(email_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM email_logs WHERE id = ?", (email_id,))
    row = cur.fetchone()
    conn.close()
    return row


def update_email_status(email_id, new_status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE email_logs SET status = ?, sent_at = datetime('now') WHERE id = ?",
        (new_status, email_id),
    )
    conn.commit()
    conn.close()


# -----------------------------------
# USERS AND TOKENS
# -----------------------------------
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


def get_all_user_ids():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users")
    rows = [row["id"] for row in cur.fetchall()]
    conn.close()
    return rows
