import sqlite3

from src.custom_exceptions import ChathistoryCountExceptionError
# -------------------- Utilities -------------------- #

def get_chat_records_count(cursor) -> int|str:
    try:
        cursor.execute("select COUNT(*) from chatbot_history LIMIT 5")
        return cursor.fetchall()[0][0]
    except sqlite3.Error as e:
        raise ChathistoryCountExceptionError("facing isssue while retriving records from the database"
                                             "Please check logs.")
    except Exception:
        raise ChathistoryCountExceptionError("something went wrong while getting chat records count."
                                             " Please check logs.")