import sqlite3

con = sqlite3.connect('cash-tracker.db', check_same_thread=False)
con.row_factory = sqlite3.Row
cur = con.cursor()

