import sqlite3

connection = sqlite3.connect('data/database.db')
cur = connection.cursor()

cur.execute('UPDATE update_state SET state=? WHERE updfunc=?', ('false', 'auto'))
connection.commit()
