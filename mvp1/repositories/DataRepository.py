from .Database import Database
from datetime import date, timedelta

today = date.today()
tomorrow = date.today() + timedelta(1)
week = date.today() - timedelta(7)
month = date.today() - timedelta(30)


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    # vul hier de verschillende functies aan om je database aan te spreken

    @staticmethod
    def read_history():
        sql = "SELECT sum(hoeveelheid) as `hoeveelheid`,meetdatum FROM tbl_metingen GROUP BY CAST(meetdatum AS DATE) ORDER BY meetdatum"
        return Database.get_rows(sql)

    @staticmethod
    def read_history_today():
        sql = "SELECT hoeveelheid,meetdatum FROM tbl_metingen WHERE meetdatum between %s and %s ORDER BY meetdatum"
        params = [today, tomorrow]
        print(today)
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_week():
        sql = "SELECT hoeveelheid,meetdatum FROM tbl_metingen WHERE meetdatum BETWEEN %s AND %s ORDER BY meetdatum"
        params = [week, tomorrow]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_feed_average(days=30):
        sql = "SELECT avg(tbl_metingen_by_day.sum_hoeveelheid_day) as `avg_hoeveelheid_day` FROM(SELECT sum(hoeveelheid) as `sum_hoeveelheid_day`, cast(meetdatum as date) as `meetdatum` FROM tbl_metingen GROUP BY CAST(meetdatum AS DATE)) as tbl_metingen_by_day"

        return Database.get_one_row(sql)

    @staticmethod
    def add_hoeveelheid(hoeveelheid):
        sql = "INSERT INTO tbl_metingen (sensor,hoeveelheid) VALUES (%s,%s)"
        params = [1, hoeveelheid]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_settings(daily_goal, daily_range):
        sql = "UPDATE tbl_settings SET daily_goal = %s, daily_range = %s WHERE IDsettings = 1"
        params = [daily_goal, daily_range]
        return Database.execute_sql(sql, params)

    @staticmethod
    def read_settings():
        sql = "SELECT daily_goal, daily_range, appname, datum FROM tbl_settings WHERE IDsettings = 1"

        return Database.get_one_row(sql)
