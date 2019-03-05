import sqlite3
from os.path import isfile
path = "data/data.db"

def create():
	if isfile(path):
		print "already a database"
	else:
		db = sqlite3.connect(path)
		cmd_account = "CREATE TABLE accounts(username TEXT PRIMARY KEY, password TEXT, phone TEXT, expecting TEXT);"
		db.execute(cmd_account)
		print "makes database here"

create()
