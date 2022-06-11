#!/usr/bin/env python3

import sqlite3

connection = sqlite3.connect('crypto.db')


with open('init_db_schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

connection.commit()
connection.close()
