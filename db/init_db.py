import sqlite3
from os.path import exists


def create_db():
    if not exists('./database.db'):
        print("ATTENTION: création d'une nouvelle base de données")
        connection = sqlite3.connect('./database.db')
        with open('./db/schema.sql') as f:
            connection.executescript(f.read())
        connection.commit()
        connection.close()
