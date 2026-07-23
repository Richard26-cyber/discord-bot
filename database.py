import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS geburtstage (
                user_id INTEGER PRIMARY KEY,
                tag     INTEGER NOT NULL,
                monat   INTEGER NOT NULL,
                jahr    INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS aktivitaet (
                user_id      INTEGER NOT NULL,
                guild_id     INTEGER NOT NULL,
                nachrichten  INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, guild_id)
            );

            CREATE TABLE IF NOT EXISTS wins (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER NOT NULL,
                text     TEXT    NOT NULL,
                datum    TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS zitate (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL,
                username  TEXT    NOT NULL,
                text      TEXT    NOT NULL,
                datum     TEXT    NOT NULL
            );
        """)
