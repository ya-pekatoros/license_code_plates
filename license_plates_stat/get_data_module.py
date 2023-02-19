import sqlite3
import requests
from bs4 import BeautifulSoup
import threading
import datetime

#keep letters file in the same folder as this file


SITE = r'https://www.fahrerbewertung.de/statistiken/kennzeichen/'

class GetData(threading.Thread):
    def __init__(self):
         super(GetData, self).__init__()

    errors = 0
    sucesses = 0
    goal = 0
    undone = 0
    status = 'Not in process'
    
    stop = False

    def run(self):
        connection = sqlite3.connect('data/database.db')
        cur = connection.cursor()
        letters = cur.execute('SELECT letter FROM letters').fetchall()
        error_count = 0
        sucess_count = 0
        undone = len(letters) - sucess_count - error_count
        cur.execute("INSERT INTO updates (letters_number, sucesses, errors, undone) VALUES (?, ?, ?, ?)",
            (len(letters), sucess_count, error_count, undone)
        )
        connection.commit()
        update_id = cur.lastrowid
        today = datetime.datetime.now().date()
        self.errors = 0
        self.sucesses = 0
        self.goal = 0
        self.undone = 0
        self.status = 'Not in process'
        for i, (letter,) in enumerate(letters):
            value = self.get_numbers(letter)
            (letter_id,) = cur.execute('SELECT id FROM letters WHERE letter=?', (letter,)).fetchone()
            self.status = 'In process'
            self.errors = error_count
            self.sucesses = sucess_count
            self.goal = len(letters)
            self.undone = len(letters) - sucess_count - error_count
            current_value = cur.execute('SELECT id FROM letter_values WHERE letter_id=? AND created_at=?', (letter_id, today)).fetchone()
            if current_value:
                (current_value_id,) = current_value
                if value:
                    cur.execute("UPDATE letter_values SET value=? WHERE id=?",
                        (value, current_value_id)
                    )
                    connection.commit()
                    sucess_count += 1
                    undone = len(letters) - sucess_count - error_count
                    cur.execute("UPDATE updates SET sucesses=?, errors=?, undone=? WHERE id=?",
                        (sucess_count, error_count, undone, update_id)
                    )
                    connection.commit()
            else:
                if not value:
                    value = 0
                    cur.execute("INSERT INTO letter_values (letter_id, value, succeded, created_at) VALUES (?, ?, ?, ?)",
                        (letter_id, value, 'FALSE', today)
                    )
                    error_count += 1
                    undone = len(letters) - sucess_count - error_count
                    connection.commit()
                    cur.execute("UPDATE updates SET sucesses=?, errors=?, undone=? WHERE id=?",
                        (sucess_count, error_count, undone, update_id)
                    )
                    connection.commit()
                else:
                    cur.execute("INSERT INTO letter_values (letter_id, value, succeded, created_at) VALUES (?, ?, ?, ?)",
                        (letter_id, value, 'TRUE', today)
                    )
                    connection.commit()
                    sucess_count += 1
                    undone = len(letters) - sucess_count - error_count
                    cur.execute("UPDATE updates SET sucesses=?, errors=?, undone=? WHERE id=?",
                        (sucess_count, error_count, undone, update_id)
                    )
                    connection.commit()
            if self.stop:
                break
        self.status = 'Not in process'
        self.errors = error_count
        self.sucesses = sucess_count
        self.goal = len(letters)
        self.undone = len(letters) - sucess_count - error_count
        connection.close()


    def get_numbers(self, l):
        url = SITE + l
        try:
            pg = requests.get(url)
            soup = BeautifulSoup(pg.text, 'html.parser')
            my_text = soup.find('div', class_='widget-note').text.strip()
            number = my_text.split()[-2]
            if not number.isnumeric():
                number = '0'
            return number
        except:
            return None
