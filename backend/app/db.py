"""SQLite init + synthetic seed. Records carry per-trial canaries."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "tickettrap.db"


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def reset_and_seed(canary_for: dict[int, str]):
    """Reset all state between trials and seed synthetic records.

    canary_for maps customer_id -> trial-specific canary string.
    """
    conn = get_conn()
    c = conn.cursor()
    c.executescript(
        """
        DROP TABLE IF EXISTS tickets;
        DROP TABLE IF EXISTS customers;
        CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, email TEXT, secret_canary TEXT);
        CREATE TABLE tickets (id INTEGER PRIMARY KEY, customer_id INTEGER, body TEXT);
        """
    )
    # TODO: seed realistic synthetic customers/tickets for each case.
    for cid, canary in canary_for.items():
        c.execute(
            "INSERT INTO customers VALUES (?,?,?,?)",
            (cid, f"Synthetic {cid}", f"user{cid}@example.test", canary),
        )
    conn.commit()
    conn.close()
