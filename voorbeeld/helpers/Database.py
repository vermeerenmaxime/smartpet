# import mysql en cursors
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor


class Database:
    def __init__(self, app, user, password, db, host='localhost', port=3306):
        # MySQL configurations
        app.config['MYSQL_DATABASE_USER'] = user
        app.config['MYSQL_DATABASE_PASSWORD'] = password
        app.config['MYSQL_DATABASE_PORT'] = port
        app.config['MYSQL_DATABASE_DB'] = db
        app.config['MYSQL_DATABASE_HOST'] = host

        mysql = MySQL(cursorclass=DictCursor)  # cursor is dict ipv tuple
        mysql.init_app(app)
        self.mysql = mysql

    def get_data(self, sql, params=None, single=False):
        # Deze routine wordt gebruikt om data op te halen.
        # Params kunnen leeg zijn
        conn = self.mysql.connect()
        cursor = conn.cursor()
        result = None

        print("Getting data")
        try:
            print(sql)
            cursor.execute(sql, params)
            conn.commit()
            if single:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(e)
        conn.close()

        # We always return the data as a big list to keep this as generic as possible 😉
        return result

    def set_data(self, sql, params=None):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        print("Creating / Updating data")
        try:
            print(sql)
            cursor.execute(sql, params)
            conn.commit()
            result = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(e)
            return f'Error: {e}'
        conn.close()

        return cursor.lastrowid

    def delete_data(self, sql, params=None):
        conn = self.mysql.connect()
        cursor = conn.cursor()
        print("Deleting data")
        try:
            print(sql)
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
        except Exception as e:
            print(e)
            return f'Error: {e}'

        conn.close()

        return cursor.rowcount
