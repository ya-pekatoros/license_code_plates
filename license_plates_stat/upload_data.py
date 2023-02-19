import sqlite3
import pandas as pd
import datetime

letters_df = pd.read_table('data/to_upload/letters_set.txt')
letters =  list(letters_df.Letters)


list_of_files = []

for i in range(18,29):
    list_of_files.append(f'{i}.02.2022.txt')

for i in range(1,4):
    list_of_files.append(f'0{i}.03.2022.txt')


for file in list_of_files:
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    values_df = pd.read_table(f'data/to_upload/{file}')
    values =  list(values_df.Values)
    for i, letter in enumerate(letters):
        (letter_id,) = cur.execute('SELECT id FROM letters WHERE letter=?', (letter,)).fetchone()
        cur.execute("INSERT INTO letter_values (letter_id, value, succeded, created_at) VALUES (?, ?, ?, ?)",
            (letter_id, values[i], 'TRUE', datetime.datetime.strptime(file[:-3], '%d.%m.%Y.').date())
        )
    connection.commit()
    connection.close()