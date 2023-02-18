import mysql.connector
import sys

class Database:
    def __init__(self, host, user, password, database):
        self.connection = None
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        if self.connection.is_connected():
            print(f"Database (%s) connection successful." %(database))
        else:
            sys.exit(f"Database (%s) connection failed." %(database))
        
    def query(self, sql):
        cursor = self.connection.cursor()
        cursor.execute(sql)
        return cursor

    def insert(self,sql):
        cursor = self.query(sql)
        id = cursor.lastrowid
        self.connection.commit()
        cursor.close()
        return id

    def update(self,sql):
        cursor = self.query(sql)
        rowcount = cursor.rowcount
        self.connection.commit()
        cursor.close()
        return rowcount

    def fetch(self, sql):
        rows = []
        cursor = self.query(sql)
        if cursor.with_rows:
            rows = cursor.fetchall()
        cursor.close()
        return rows

    def __del__(self):
        if self.connection != None:
            self.connection.close()