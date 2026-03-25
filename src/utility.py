import sqlite3
import logging
from src.custom_exceptions import ChathistoryCountExceptionError

logger=logging.getLogger("Utility")

# -------------------- Utilities -------------------- #

def get_chat_records_count(cursor) -> int | str:
    logger.info("Starting retrieval of chat records count from chatbot_history table.")

    try:
        logger.info("Executing COUNT query on chatbot_history table.")
        cursor.execute("SELECT COUNT(*) FROM chatbot_history LIMIT 5")

        result = cursor.fetchall()

        if not result:
            logger.warning("No records returned from chatbot_history table.")
            return 0

        count = result[0][0]
        logger.info(f"Successfully retrieved chat records count: {count}")

        return count

    except sqlite3.Error as e:
        logger.exception("Database error occurred while retrieving chat records count.")
        raise ChathistoryCountExceptionError(
            "Facing issue while retrieving records from the database. Please check logs."
        )

    except Exception as e:
        logger.exception("Unexpected error occurred while getting chat records count.")
        raise ChathistoryCountExceptionError(
            "Something went wrong while getting chat records count. Please check logs."
        )