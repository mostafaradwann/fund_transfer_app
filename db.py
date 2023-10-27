#import sqlite module
import sqlite3
# create database and Connect

db = sqlite3.connect("accounts.db")
# setting up cursor
cr = db.cursor()
#create table 
sql_query = """CREATE TABLE if not exists accounts (
    id text PRIMARY KEY,
    name text NOT NULL, 
    balance float NOT NULL
    )"""
cr.execute(sql_query)

#Commit changes
db.commit()

#Close Database
db.close