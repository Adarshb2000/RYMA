import sqlite3
from helpers import val
import ast

conn_awards = sqlite3.connect("awards.db")
award = conn_awards.cursor()
conn = sqlite3.connect("students.db")
db = conn.cursor()

#answer = input()
with conn:
    db.execute("UPDATE y19_btech_bs SET votes = ''")
with conn_awards:
    award.execute("UPDATE season_01 SET nominees = ''")

#answer = answer.lower()
info = db.execute("SELECT * FROM y19_btech_bs WHERE id='190050'").fetchall()
print(info)

"""db.execute(f"UPDATE y19_btech_bs SET email='abaderia31@outlook.com' WHERE id='{answer}'")
db.execute("UPDATE y19_btech_bs SET votes=''")"""

conn_awards.close()

