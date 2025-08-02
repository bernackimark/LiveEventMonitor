from contextlib import contextmanager

from config import CONN_STR_UNPACKED
import psycopg2
from psycopg2.extras import RealDictCursor


@contextmanager
def get_cursor_w_commit():
    """Using raw psycopg2, connect to & yield a database connection.  Commits the transaction, if no error"""
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(CONN_STR_UNPACKED)
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        # Roll back in case of exception
        if conn:
            conn.rollback()
        raise
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@contextmanager
def get_cursor_as_real_dict_obj():
    """Using raw psycopg2, connect to & yield a database connection.  Ex usage:
    c.execute("SELECT * FROM my_table WHERE id = %s", (1,))
    row = c.fetchone()
    row_as_dict: dict = dict(row)
    """
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(CONN_STR_UNPACKED)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        yield cursor
    except Exception as e:
        # Roll back in case of exception
        if conn:
            conn.rollback()
        raise
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
