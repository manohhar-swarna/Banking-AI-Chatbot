import os
import sqlite3

# -------------------- Methods -------------------- #
def make_db_table()->None:
    """create the database and default table"""
    connection = sqlite3.connect(os.path.join(os.getcwd(), "DB/employe.db"))
    cursor = connection.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS emp
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       NOT
                       NULL,
                       email
                       TEXT
                       UNIQUE,
                       type
                       INTEGER
                       NOT
                       NULL
                       CHECK (
                       type
                       IN
                   (
                       0,
                       1
                   ))
                       );
                   """)

    cursor.execute("""INSERT INTO emp (id, name, email, type)
                      VALUES (?, ?, ?, ?)""", (1, "sam", "sam@gmail.com", False))
    cursor.execute("""INSERT INTO emp (id, name, email, type)
                      VALUES (?, ?, ?, ?)""", (2, "jon", "jon@gmail.com", False))
    cursor.execute("""INSERT INTO emp (id, name, email, type)
                      VALUES (?, ?, ?, ?)""", (3, "priya", "priya@gmail.com", True))
    cursor.execute("""INSERT INTO emp (id, name, email, type)
                      VALUES (?, ?, ?, ?)""", (4, "manu", "manu@gmail.com", False))

    connection.commit()
    connection.close()


def create_employee_db_table()->None:
    "It will create the employee database and create table emp with predefined records"
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
    create_employee_db_table()

if __name__ == "__main__":
    main()







