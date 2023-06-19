import sqlite3
from flask import g

def connect_to_database():
    sql = sqlite3.connect("C:/Users/Nandhini kesavan/Desktop/final yr project/login-reg-db/logreg.db")
    sql.row_factory = sqlite3.Row
    return sql



def getDatabase():
    if not hasattr(g, "logreg"):
        g.logreg = connect_to_database()
    return g.logreg