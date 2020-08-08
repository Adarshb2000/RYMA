import sqlite3
from helpers import val
import ast

conn_awards = sqlite3.connect("awards.db")
award = conn_awards.cursor()
conn = sqlite3.connect("students.db")
db = conn.cursor()
with conn:
    conn.row_factory = lambda cursor, row : row[0]
    db_row = conn.cursor()


#answer = answer.lower()
names = db_row.execute("SELECT name FROM y19_btech_bs").fetchall()
for name in names:
    name = name.split(' ')
    if len(name[0]) > 10:
        print(name)

ada = input()

print(ada[3:6])


"""db.execute(f"UPDATE y19_btech_bs SET email='abaderia31@outlook.com' WHERE id='{answer}'")
db.execute("UPDATE y19_btech_bs SET votes=''")"""

conn_awards.close()

