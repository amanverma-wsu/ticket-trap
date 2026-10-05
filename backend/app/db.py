"""SQLite persistence; state is reset and reseeded between trials.
DB path comes from TICKETTRAP_DB if set, else data/tickettrap.db at the repo root."""
import os
import sqlite3
from pathlib import Path

from .models import CustomerRecord, Ticket


def db_path() -> Path:
    override = os.environ.get("TICKETTRAP_DB")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "data" / "tickettrap.db"


def get_conn() -> sqlite3.Connection:
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def reset_and_seed(customers: list[CustomerRecord], ticket: Ticket) -> None:
    conn = get_conn()
    try:
        conn.executescript(
            """
            DROP TABLE IF EXISTS customers;
            DROP TABLE IF EXISTS tickets;
            DROP TABLE IF EXISTS reports;
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY, name TEXT, email TEXT, secret_canary TEXT
            );
            CREATE TABLE tickets (
                id INTEGER PRIMARY KEY, customer_id INTEGER, body TEXT
            );
            CREATE TABLE reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER, destination TEXT, content TEXT
            );
            """
        )
        for c in customers:
            conn.execute(
                "INSERT INTO customers (id, name, email, secret_canary) VALUES (?, ?, ?, ?)",
                (c.id, c.name, c.email, c.secret_canary),
            )
        conn.execute(
            "INSERT INTO tickets (id, customer_id, body) VALUES (?, ?, ?)",
            (ticket.id, ticket.customer_id, ticket.body),
        )
        conn.commit()
    finally:
        conn.close()


def get_ticket(ticket_id: int) -> Ticket | None:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, customer_id, body FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
        return Ticket(**dict(row)) if row else None
    finally:
        conn.close()


def get_customer(customer_id: int) -> CustomerRecord | None:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, name, email, secret_canary FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
        return CustomerRecord(**dict(row)) if row else None
    finally:
        conn.close()


def record_report(ticket_id: int, destination: str, content: str) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO reports (ticket_id, destination, content) VALUES (?, ?, ?)",
            (ticket_id, destination, content),
        )
        conn.commit()
    finally:
        conn.close()


def list_reports() -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT ticket_id, destination, content FROM reports ORDER BY id"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
