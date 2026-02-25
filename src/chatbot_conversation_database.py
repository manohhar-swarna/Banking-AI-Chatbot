import os
import sqlite3

# -------------------- Methods -------------------- #

def make_db_table()->None:
    """this method will create the chatbot conversation database and default table"""
    connection = sqlite3.connect(os.path.join(os.getcwd(), "DB/chatbot_conversation.db"))
    cursor = connection.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS chatbot_history
                   ( user_query TEXT NOT NULL,
                       bot_response TEXT NOT NULL
                   )
                   """)
    connection.commit()
    connection.close()

def create_chatbot_conversation_db_table()->None:
    """Create the chatbot conversation database and table chatbot_history
       and store all the chatbot conversation data into the table chatbot_history"""
    try:
        if not os.path.exists(os.path.join(os.getcwd(), "DB")):
            os.mkdir(os.path.join(os.getcwd(), "DB"))
            make_db_table()
        else:
            make_db_table()

    except Exception as e:
        print("the exception occured due to the error : {}".format(e))


# -------------------- Main App -------------------- #

def main()->None:
    "code orchestration method"
    create_chatbot_conversation_db_table()

if __name__ == "__main__":
    main()
