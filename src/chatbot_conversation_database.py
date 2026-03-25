import os
import sqlite3
import logging

from src.log import setup_logging

# -------------------- Methods -------------------- #

def make_db_table() -> None:
    """this method will create the chatbot conversation database and default table"""
    logger.info("Starting database and table creation process.")

    db_path = os.path.join(os.getcwd(), "DB/chatbot_conversation.db")
    logger.info(f"Database path resolved: {db_path}")

    try:
        connection = sqlite3.connect(db_path)
        logger.info("Database connection established successfully.")

        cursor = connection.cursor()
        logger.info("Executing CREATE TABLE query for chatbot_history.")

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS chatbot_history
                       ( user_query TEXT NOT NULL,
                         bot_response TEXT NOT NULL
                       )
                       """)

        connection.commit()
        logger.info("Table creation committed successfully.")

        connection.close()
        logger.info("Database connection closed successfully.")

    except Exception as e:
        logger.exception("Error occurred while creating database/table.")


def create_chatbot_conversation_db_table() -> None:
    """Create the chatbot conversation database and table chatbot_history
       and store all the chatbot conversation data into the table chatbot_history"""
    logger.info("Starting chatbot conversation DB setup process.")

    db_dir = os.path.join(os.getcwd(), "DB")
    logger.info(f"Checking if DB directory exists at path: {db_dir}")

    try:
        if not os.path.exists(db_dir):
            logger.info("DB directory does not exist. Creating directory.")
            os.mkdir(db_dir)
            logger.info("DB directory created successfully.")

            make_db_table()
        else:
            logger.info("DB directory already exists. Proceeding to create table if not exists.")
            make_db_table()

    except Exception as e:
        logger.exception("Error occurred during chatbot DB setup process.")
        print("the exception occurred due to the error : {}".format(e))


# -------------------- Main App -------------------- #

def main() -> None:
    "code orchestration method"
    logger.info("Application started. Initializing chatbot DB setup.")

    try:
        create_chatbot_conversation_db_table()
        logger.info("Chatbot DB setup completed successfully.")

    except Exception as e:
        logger.exception("Unexpected error occurred in main execution.")


if __name__ == "__main__":
    setup_logging()
    logger=logging.getLogger("chatbot_conversation_db")
    logger.info("Running application entry point.")
    main()
