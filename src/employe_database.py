import sqlite3

connection=sqlite3.connect("employe.db")
cursor=connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS emp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    type INTEGER NOT NULL CHECK (type IN (0, 1))
)
""")

cursor.execute("""INSERT INTO emp (id, name, email, type) VALUES (?, ?, ?, ?)""",(1, "sam","sam@gmail.com",False))
cursor.execute("""INSERT INTO emp (id, name, email, type) VALUES (?, ?, ?, ?)""",(2, "jon","jon@gmail.com",False))
cursor.execute("""INSERT INTO emp (id, name, email, type) VALUES (?, ?, ?, ?)""",(3, "priya","priya@gmail.com",True))
cursor.execute("""INSERT INTO emp (id, name, email, type) VALUES (?, ?, ?, ?)""",(4, "manu","manu@gmail.com",False))

connection.commit()
connection.close()


