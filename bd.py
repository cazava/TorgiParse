from datetime import datetime

import psycopg2
from psycopg2 import sql, Error


class Bd:
    def __init__(self):
        self.db_params = {
            'host': 'postgres',  # или IP-адрес сервера
            'database': 'postgres',
            'user': 'postgres',
            'password': 'Kawabanga17'
        }
        self.connection = psycopg2.connect(**self.db_params)
        self.cursor = self.connection.cursor()
        # Параметры подключения к базе данных

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
                posted SMALLINT,
                photo_url TEXT
                )
                ''')
        self.connection.commit()

    def create(self, id, address, lotstatus, pricemin, biddendtime, square, kadnum, ref, photo_url, posted=False):
        with self.connection:
            try:
                self.cursor.execute(
                    "INSERT INTO lots (id, address, lotStatus, priceMin, biddEndTime, square, kadNum, ref, posted, photo_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (id, address, lotstatus, pricemin, biddendtime, square, kadnum, ref, posted, photo_url)
                )
            except Error as e:
                print(f"Ошибка: {e} {id}")

    def check(self, id):
        with self.connection:
            self.cursor.execute(
                "SELECT * FROM lots WHERE id = %s", (id,)
            )
            query = self.cursor.fetchone()
        return query

    def check_kad(self, kadnum):
        with self.connection:
            self.cursor.execute(
                "SELECT * FROM lots WHERE kadnum = %s", (kadnum,)
            )
        return self.cursor.fetchone()

    def get_lot(self, kadnum):
        with self.connection:
            self.cursor.execute(
                "SELECT * FROM lots WHERE kadNum = %s", (kadnum,)
            )
            query = self.cursor.fetchone()
        return query[0]

    def ref(self, id):
        with self.connection:
            self.cursor.execute(
                "SELECT ref FROM lots WHERE id = %s;", (id,)
            )
            res = self.cursor.fetchone()[0]
        return f'https://torgi.gov.ru/new/public/lots/lot/' + str(res)

    def koord_add(self, id, lon, lat):
        lat = str(lat)
        lon = str(lon)
        with self.connection:
            self.cursor.execute(
                "UPDATE lots SET lon = %s, lat = %s WHERE id =%s", (lon, lat, id)
            )

    def upd_expire(self):
        with self.connection:
            today = datetime.now()

            self.cursor.execute("SELECT * FROM lots")
            query = self.cursor.fetchall()
            for exp in query:
                print(exp)
                exp_lot = exp[0]
                date = datetime.strptime(exp[4], '%d-%m-%Y %H:%M:%S')
                if date <= today:
                    self.cursor.execute("DELETE FROM lots WHERE id = %s", (exp_lot,))

    def get_lots(self):
        with self.connection:
            self.cursor.execute("SELECT * FROM lots;")
            query = self.cursor.fetchall()
            return query

    def set_post(self, lot_id):
        with self.connection:
            self.cursor.execute("UPDATE lots SET posted = 1 WHERE id = %s", (lot_id,))

    def close(self):
        self.cursor.close()
        self.connection.close()

    def counts(self):
        with self.connection:
            self.cursor.execute("SELECT COUNT(*) FROM lots;")
            return self.cursor.fetchone()

    def clear(self):
        with self.connection:
            self.cursor.execute("TRUNCATE TABLE lots CASCADE;")

# Создание экземпляра класса Bd с параметрами подключения
lotsbd = Bd()
