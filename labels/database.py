import os
from typing import Union

import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_cursor(return_conn: bool = False) -> Union[pyodbc.Cursor, None]:
    """
    This function creates a connection to the database.

    Parameters
    ----------
    return_conn : bool, optional
        If True, the function returns the connection to the database,
        by default False.
    Returns
    -------
    pyodbc.Connection
        The connection to the database.
    """
    try:
        # Establish the connection
        conn = pyodbc.connect(
            f"""DRIVER=ODBC Driver 18 for SQL Server;\
            SERVER={os.getenv("SERVER")};\
            DATABASE={os.getenv("DATABASE")};\
            UID={os.getenv("USERNAME")};\
            PWD={os.getenv("PASSWORD")}"""
        )
        cursor = conn.cursor()
        return cursor if not return_conn else (conn, cursor)
    except Exception:
        return None
