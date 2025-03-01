import sqlite3

class ConnectionManager:
    def __init__(self, database):
        self.con = sqlite3.connect(database)
        self.cursor = self.con.cursor()
    
    def execute(self, sql, *args, **kwargs):
        sql = self.cursor.execute(sql, *args, **kwargs)
        return sql
    
    def executescript(self, sql, *args, **kwargs):
        sql = self.cursor.executescript(sql, *args, **kwargs)
        return sql
    
    def commit(self):
        self.con.commit()
        
db = ConnectionManager("database.db")