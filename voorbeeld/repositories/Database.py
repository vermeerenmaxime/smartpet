from mysql import connector  # pip install mysql-connector-python
import os


class Database:

    # 1. connectie openen met classe variabelen voor hergebruik
    @staticmethod
    def __open_connection():
        try:
            Database.db = connector.connect(
                option_files=os.path.abspath(os.path.join(
                    os.path.dirname(__file__), "../config.py")),
                autocommit=False
            )
            if "AttributeError" in(str(type(Database.db))):
                raise Exception("foutieve database parameters in config")
            Database.cursor = Database.db.cursor(
                dictionary=True, buffered=True)  # lazy loaded
        except connector.Error as err:
            if err.errno == connector.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error: Er is geen toegang tot de database")
            elif err.errno == connector.errorcode.ER_BAD_DB_ERROR:
                print("Error: De database is niet gevonden")
            else:
                print(err)
            return

    # 2. Executes READS
    @staticmethod
    def get_rows(sqlQuery, params=None):
        result = None
        Database.__open_connection()
        try:
            Database.cursor.execute(sqlQuery, params)
            result = Database.cursor.fetchall()
            Database.cursor.close()
            if (result is None):
                print(ValueError(f"Resultaten zijn onbestaand.[DB Error]"))
            Database.db.close()
        except Exception as error:
            print(error)  # development boodschap
            result = None
        finally:
            return result

    @staticmethod
    def get_one_row(sqlQuery, params=None):
        Database.__open_connection()
        try:
            Database.cursor.execute(sqlQuery, params)
            result = Database.cursor.fetchone()
            Database.cursor.close()
            if (result is None):
                raise ValueError("Resultaten zijn onbestaand.[DB Error]")
        except Exception as error:
            print(error)  # development boodschap
            result = None
        finally:
            Database.db.close()
            return result

    # 3. Executes INSERT, UPDATE, DELETE with PARAMETERS
    @staticmethod
    def execute_sql(sqlQuery, params=None):
        result = None
        Database.__open_connection()
        try:
            Database.cursor.execute(sqlQuery, params)
            Database.db.commit()
            # bevestigig van create (int of 0)
            result = Database.cursor.lastrowid
            # bevestiging van update, delete (array)
            # result = result if result != 0 else params  # Extra controle doen!!
            if result != 0:  # is een insert, deze stuur het lastrowid terug.
                result = result
            else:  # is een update of een delete
                if Database.cursor.rowcount == -1:  # Er is een fout in de SQL
                    raise Exception("Fout in SQL")
                elif Database.cursor.rowcount == 0:  # Er is niks gewijzigd, where voldoet niet of geen wijziging in de data
                    result = 0
                elif result == "undefined":  # Hoeveel rijen werden gewijzigd
                    raise Exception("SQL error")
                else:
                    result = Database.cursor.rowcount
        except connector.Error as error:
            Database.db.rollback()
            result = None
            print(f"Error: Data niet bewaard.{error.msg}")
        finally:
            Database.cursor.close()
            Database.db.close()
            return result
