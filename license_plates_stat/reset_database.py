import sqlite3
import pandas as pd


def recreate_letters_table():
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    letters_drop = f'DROP TABLE IF EXISTS letters'
    letters_create = (
        f'CREATE TABLE letters (id INTEGER PRIMARY KEY AUTOINCREMENT,'
        f'letter TEXT)'
    )

    cur.execute(letters_drop)
    print(letters_drop)

    cur.execute(letters_create)
    print(letters_create)

    connection.commit()
    connection.close()
    return


def recreate_values_table():
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    values_drop = f'DROP TABLE IF EXISTS letter_values'
    values_create = (
        f'CREATE TABLE letter_values (id INTEGER PRIMARY KEY AUTOINCREMENT,'
        f'letter_id INTEGER NOT NULL,'
        f'created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
        f'value INTEGER,'
        f'succeded TEXT,'
        f'FOREIGN KEY (letter_id) REFERENCES letters (id))'
    )

    cur.execute(values_drop)
    print(values_drop)

    cur.execute(values_create)
    print(values_create)

    connection.commit()
    connection.close()
    return


def recreate_updates_table():
    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    values_drop = f'DROP TABLE IF EXISTS updates'
    values_create = (
        f'CREATE TABLE updates (id INTEGER PRIMARY KEY AUTOINCREMENT,'
        f'letters_number INTEGER NOT NULL,'
        f'created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,'
        f'sucesses INTEGER,'
        f'undone INTEGER,'
        f'errors INTEGER)'
    )

    cur.execute(values_drop)
    print(values_drop)

    cur.execute(values_create)
    print(values_create)

    connection.commit()
    connection.close()
    return


def fill_up_letter_table():
    #keep letters file in the same folder as this file
    letters_df = pd.read_table('data/letters.txt')
    letters =  list(letters_df.Letters)

    connection = sqlite3.connect('data/database.db')
    cur = connection.cursor()
    
    for letter in letters:
        cur.execute('INSERT INTO letters (letter) VALUES (?)', (letter,))
        print(f'{letter} inserted in DB')
    connection.commit()
    connection.close()
    return

if __name__ == "__main__":
    recreate_letters_table()
    recreate_values_table()
    recreate_updates_table()
    fill_up_letter_table()
    print('Database sucessfully recreated!')
