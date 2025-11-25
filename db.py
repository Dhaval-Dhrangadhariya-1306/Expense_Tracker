import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "expenses.db"

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                note TEXT
            )
        """)
        conn.commit()

def add_expense(date, category, amount, note=""):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
                    (date, category, amount, note))
        conn.commit()
        return cur.lastrowid

def update_expense(expense_id, date, category, amount, note=""):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE expenses SET date=?, category=?, amount=?, note=? WHERE id=?",
                     (date, category, amount, note, expense_id))
        conn.commit()

def delete_expense(expense_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
        conn.commit()

def fetch_expenses(where_clause="", params=()):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        query = "SELECT id, date, category, amount, note FROM expenses"
        if where_clause:
            query += " WHERE " + where_clause
        query += " ORDER BY date DESC"
        cur.execute(query, params)
        return cur.fetchall()

def fetch_monthly_summary(year_month):
    # year_month like '2025-11' to filter by prefix of date (YYYY-MM)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT category, SUM(amount) FROM expenses 
            WHERE date LIKE ? GROUP BY category
        """, (f"{year_month}%",))
        return cur.fetchall()
