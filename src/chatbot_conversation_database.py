import sqlite3

connection=sqlite3.connect("chatbot_conversation.db")
cursor=connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS chatbot_history (
    user_query TEXT NOT NULL,
    bot_response TEXT NOT NULL)
""")
connection.commit()
connection.close()