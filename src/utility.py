import sqlite3

# -------------------- Utilities -------------------- #

def get_chat_records_count(cursor) -> int|str:
    try:
        cursor.execute("select COUNT(*) from chatbot_history LIMIT 5")
        return cursor.fetchall()[0][0]
    except sqlite3.Error as e:
        return "facing isssue while retriving records from the database/table"