from contextlib import contextmanager
import os.path
import sqlite3


@contextmanager
def open_db():
    try:
        db_name = os.path.join("db", "db.db")
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        yield cursor
    finally:
        conn.commit()
        conn.close()


def _init_db():
    with open(os.path.join("db", "schema.sql")) as f, open_db() as cursor:
        script = f.read()
        cursor.executescript(script)


_init_db()
