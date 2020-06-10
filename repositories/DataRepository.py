# pylint: skip-file
from .Database import Database
from datetime import date, timedelta,datetime

today = date.today()
tomorrow = date.today() + timedelta(1)
week = date.today() - timedelta(7)
month = date.today() - timedelta(30)
year = date.today() - timedelta(365)


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
    def read_metingen():
        sql = "SELECT hoeveelheid,meetdatum,actiecode,device,beschrijving,meeteenheid FROM tbl_metingen m LEFT JOIN tbl_devices d ON d.IDdevice = m.device_id ORDER BY meetdatum DESC"
        return Database.get_rows(sql)

    @staticmethod
    def read_history():
        sql = "SELECT hoeveelheid,meetdatum FROM tbl_metingen WHERE device_id = 1 AND actiecode = 'REMOVE' ORDER BY meetdatum"
        return Database.get_rows(sql)

    @staticmethod
    def read_history_day():
        sql = "SELECT sum(hoeveelheid) as `hoeveelheid`,count(meetdatum) as `aantal` ,meetdatum FROM tbl_metingen WHERE device_id = 1 AND actiecode = 'REMOVE' AND meetdatum between %s and %s GROUP BY concat(hour(meetdatum),minute(meetdatum))"
        params = [today, tomorrow]
        #print(Database.get_rows(sql, params))
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_week():
        sql = "SELECT sum(hoeveelheid) as `hoeveelheid`,meetdatum FROM tbl_metingen WHERE device_id = 1 AND actiecode = 'REMOVE' AND meetdatum BETWEEN %s AND %s GROUP BY CAST(meetdatum AS DATE) ORDER BY meetdatum"
        params = [week, tomorrow]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_month():
        sql = "SELECT sum(hoeveelheid) as `hoeveelheid`,meetdatum,month(meetdatum) as `month` FROM tbl_metingen WHERE device_id = 1 AND actiecode = 'REMOVE' AND meetdatum BETWEEN %s AND %s GROUP BY month(meetdatum) ORDER BY meetdatum"
        params = [month, tomorrow]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_year():
        sql = "SELECT sum(hoeveelheid) as `hoeveelheid`,meetdatum, year(meetdatum) as `year` FROM tbl_metingen WHERE device_id = 1 AND actiecode = 'REMOVE' AND meetdatum BETWEEN %s AND %s GROUP BY year(meetdatum) ORDER BY meetdatum"
        params = [year, tomorrow]
        return Database.get_rows(sql, params)

    @staticmethod
    def read_history_date(datum):
        sql = "SELECT sum(hoeveelheid) as `hoeveelheid`,count(meetdatum) as `aantal` ,meetdatum FROM tbl_metingen WHERE device_id = 1 AND actiecode = 'REMOVE' AND meetdatum between %s and %s GROUP BY concat(hour(meetdatum),minute(meetdatum))"  
        params = [datum, (datetime.strptime(datum,"%Y-%m-%d")+timedelta(1))]
        #print(Database.get_rows(sql, params))
        return Database.get_rows(sql, params)

    @staticmethod
    def read_fillhistory_day():
        sql = "SELECT hoeveelheid,meetdatum,meeteenheid FROM tbl_metingen m LEFT JOIN tbl_devices d ON d.IDdevice = m.device_id WHERE device_id = 1 AND actiecode = 'ADD' AND meetdatum between %s and %s ORDER BY meetdatum DESC"
        params = [week, tomorrow]

        return Database.get_rows(sql, params)

        
        

    @staticmethod
    def read_feed_average(days):
        sql = "SELECT avg(tbl_metingen_by_day.sum_hoeveelheid_day) as `avg_hoeveelheid_day` FROM(SELECT sum(hoeveelheid) as `sum_hoeveelheid_day`, cast(meetdatum as date) as `meetdatum` FROM tbl_metingen WHERE device_id = 1 AND actiecode = 'REMOVE' GROUP BY CAST(meetdatum AS DATE)) as tbl_metingen_by_day"

        return Database.get_one_row(sql)

    @staticmethod
    def read_feed_count_today(days):
        sql = "SELECT count(idmeting) as 'count_eats',device_id,meetdatum FROM `tbl_metingen` where actiecode = 'remove' and day(meetdatum)= day(now()) group by day(meetdatum)"

        return Database.get_one_row(sql)



    @staticmethod
    def add_hoeveelheid(hoeveelheid):
        sql = "INSERT INTO tbl_metingen (device_id,hoeveelheid,actiecode) VALUES (%s,%s,%s)"
        params = [1, hoeveelheid,"ADD"]
        return Database.execute_sql(sql, params)

    @staticmethod
    def add_eaten(hoeveelheid):
        sql = "INSERT INTO tbl_metingen (device_id,hoeveelheid,actiecode) VALUES (%s,%s,%s)"
        params = [1, hoeveelheid,"REMOVE"]
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

    @staticmethod
    def ldr_inlezen(hoeveelheid):
        sql = "INSERT INTO tbl_metingen (device_id,hoeveelheid,actiecode) VALUES (%s,%s,%s)"
        params = [4, hoeveelheid, "CHECK"]
        return Database.execute_sql(sql, params)

    @staticmethod
    def servo_on():
        sql = "INSERT INTO tbl_metingen (device_id,hoeveelheid,actiecode) VALUES (%s,%s,%s)"
        params = [5, 0, "ON"]
        return Database.execute_sql(sql, params)

    @staticmethod
    def servo_off():
        sql = "INSERT INTO tbl_metingen (device_id,hoeveelheid,actiecode) VALUES (%s,%s,%s)"
        params = [5, 0, "OFF"]
        return Database.execute_sql(sql, params)
