import sqlite3
connection = sqlite3.connect("employe.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM emp")

r=cursor.fetchall()
print(r[0][0])
print(r[1][0])
print(r[0][1])
print(r[1][1])
connection.close()
