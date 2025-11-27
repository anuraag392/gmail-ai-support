from typing import Dict, Any
from app.database.db import get_connection


def get_customer_data_from_erp(from_email: str = "", email_text: str = "") -> Dict[str, Any]:
    """
    ERP/DB lookup using SQLite.
    - Looks up customer by email.
    - Fetches latest order & ticket for that customer.
    You can populate 'customers', 'orders', 'tickets' tables manually or from your system.
    """
    data = {}

    if not from_email:
        return data

    with get_connection() as conn:
        cur = conn.cursor()

        # Customer
        cur.execute(
            "SELECT name, email, phone, notes FROM customers WHERE email = ?",
            (from_email,),
        )
        cust = cur.fetchone()
        if cust:
            data["customer"] = {
                "name": cust["name"],
                "email": cust["email"],
                "phone": cust["phone"],
                "notes": cust["notes"],
            }

        # Latest order (if any)
        cur.execute(
            """
            SELECT order_id, status, expected_delivery
            FROM orders
            WHERE customer_email = ?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (from_email,),
        )
        order = cur.fetchone()
        if order:
            data["last_order"] = {
                "order_id": order["order_id"],
                "status": order["status"],
                "expected_delivery": order["expected_delivery"],
            }

        # Latest ticket (if any)
        cur.execute(
            """
            SELECT ticket_id, status, topic
            FROM tickets
            WHERE customer_email = ?
            ORDER BY rowid DESC
            LIMIT 1
            """,
            (from_email,),
        )
        ticket = cur.fetchone()
        if ticket:
            data["open_ticket"] = {
                "ticket_id": ticket["ticket_id"],
                "status": ticket["status"],
                "topic": ticket["topic"],
            }

    return data
