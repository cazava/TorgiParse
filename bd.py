import sqlite3
import geocoder as geo
import pandas as pd
from datetime import datetime


def format_datetime(datetime_str):
    # Преобразуем строку в объект datetime
    try:
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
    except:
        dt = datetime.strptime(datetime_str[:-1], '%Y-%m-%dT%H:%M:%S%z')
    # Форматируем в нужный вид
    return dt.strftime('%d-%m-%Y')


class Bd:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS lots (
                id TEXT NOT NULL PRIMARY KEY,
                address TEXT,
                lotStatus TEXT,
                priceMin INTEGER,
                biddEndTime TEXT,
                square INTEGER,
                kadNum TEXT,
                ref TEXT,
                lon TEXT,
                lat TEXT,
                posted INTEGER,
                photo_url TEXT
                
                )
                ''')

    def create(self, id, address, lotstatus, pricemin, biddendtime, square, kadnum, ref, photo_url, posted=False):
        with self.connection:
            try:
                self.cursor.execute(
                    "INSERT INTO lots (id, address, lotStatus, priceMin, biddEndTime, square, kadNum, ref, posted, photo_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (id, address, lotstatus, pricemin, biddendtime, square, kadnum, ref, posted, photo_url)
                )
            except sqlite3.Error as e:
                print(f"Ошибка: {e} {id}")

    def check(self, id):
        with self.connection:
            res = self.cursor.execute(
                "SELECT * FROM lots WHERE id = ?", (id,)
            ).fetchone()
        return res

    def check_kad(self, kadnum):
        with self.connection:
            res = self.cursor.execute(
                "SELECT * FROM lots WHERE kadnum = ?", (kadnum,)
            )
        return res.fetchone()

    def get_lot(self, id):
        with self.connection:
            res = self.cursor.execute(
                "SELECT * FROM lots WHERE kadNum = ?", (id,)
            ).fetchone()
        return res[0]

    def ref(self, id):
        with self.connection:
            res = self.cursor.execute(
                "SELECT id FROM lots WHERE id = ?", (id,)
            ).fetchone()[0]
        return f'https://torgi.gov.ru/new/public/lots/lot/' + str(res)

    def koord_add(self, id, lon, lat):
        with self.connection:
            res = self.cursor.execute(
                "UPDATE lots SET lon = ?, lat = ? WHERE id =?", (lon, lat, id)
            )

    def upd_expire(self):
        with self.connection:
            today = datetime.now()

            query = self.cursor.execute("SELECT * FROM lots").fetchall()
            for exp in query:
                exp_lot = exp[0]
                date = datetime.strptime(exp[4], '%d-%m-%Y %H:%M:%S')
                if date <= today:
                    self.cursor.execute("DELETE FROM lots WHERE id = ?", (exp_lot,))

    def get_lots(self):
        with self.connection:
            query = self.cursor.execute("SELECT * FROM lots").fetchall()
            return query

    def set_post(self, lot_id):
        with self.connection:
            self.cursor.execute("UPDATE lots SET posted = 1 WHERE id = ?", (lot_id,))

    # def change_time(self):
    #
    #     lots = self.get_lots()
    #     for lot in lots:
    #         id = lot[0]
    #         time = lot[4]
    #         new_time = format_datetime(time)
    #
    #         with self.connection:
    #             self.cursor.execute("UPDATE lots SET biddEndTime = ? WHERE id = ?", (new_time, id))


lotsbd = Bd('lots.db')
