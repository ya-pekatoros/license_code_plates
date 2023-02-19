import sqlite3

connection = sqlite3.connect('data/database.db')
cur = connection.cursor()
print(cur.execute('SELECT created_at FROM letter_values WHERE letter_id=1').fetchall())