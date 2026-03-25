import os
import sqlite3
import logging

from src.log import setup_logging

# -------------------- Methods -------------------- #
def make_db_table() -> None:
    """create the database and default table"""
    logger.info("Starting employee database and table creation process.")

    db_path = os.path.join(os.getcwd(), "DB/employe.db")
    logger.info(f"Resolved database path: {db_path}")

    try:
        connection = sqlite3.connect(db_path)
        logger.info("Database connection established successfully.")

        cursor = connection.cursor()
        logger.info("Executing CREATE TABLE query for emp.")

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS emp
                       (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL,
                           email TEXT UNIQUE,
                           type INTEGER NOT NULL CHECK (type IN (0, 1))
                       );
                       """)

        logger.info("Table ensured successfully. Inserting default records.")

        cursor.execute("""INSERT INTO emp (id, name, email, type)
                          VALUES (?, ?, ?, ?)""", (1, "sam", "sam@gmail.com", False))
        cursor.execute("""INSERT INTO emp (id, name, email, type)
                          VALUES (?, ?, ?, ?)""", (2, "jon", "jon@gmail.com", False))
        cursor.execute("""INSERT INTO emp (id, name, email, type)
                          VALUES (?, ?, ?, ?)""", (3, "priya", "priya@gmail.com", True))
        cursor.execute("""INSERT INTO emp (id, name, email, type)
                          VALUES (?, ?, ?, ?)""", (4, "manu", "manu@gmail.com", False))

        connection.commit()
        logger.info("Default employee records inserted and committed successfully.")

        connection.close()
        logger.info("Database connection closed successfully.")

    except Exception as e:
        logger.exception("Error occurred while creating employee database/table or inserting records.")


def create_employee_db_table() -> None:
    "It will create the employee database and create table emp with predefined records"
    logger.info("Starting employee DB setup process.")

    db_dir = os.path.join(os.getcwd(), "DB")
    logger.info(f"Checking if DB directory exists at: {db_dir}")

    try:
        if not os.path.exists(db_dir):
            logger.info("DB directory does not exist. Creating directory.")
            os.mkdir(db_dir)
            logger.info("DB directory created successfully.")

            make_db_table()
        else:
            logger.info("DB directory already exists. Proceeding with DB/table creation.")
            make_db_table()

    except Exception as e:
        logger.exception("Error occurred during employee DB setup process.")
        print("the exception occurred due to the error : {}".format(e))


# -------------------- Main App -------------------- #

def main() -> None:
    "code orchestration method"
    logger.info("Application started. Initializing employee DB setup.")

    try:
        create_employee_db_table()
        logger.info("Employee DB setup completed successfully.")

    except Exception as e:
        logger.exception("Unexpected error occurred in main execution.")


if __name__ == "__main__":
    setup_logging()
    logger=logging.getLogger("Employee_DB")
    logger.info("Running application entry point.")
    main()






