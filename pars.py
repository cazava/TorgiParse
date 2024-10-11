import time

import urllib3

import requests
import xml.etree.ElementTree as ET
from bd import lotsbd
import geocoder as geo
from datetime import datetime, timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# удаление дубликатов слов в строке адреса для геокодирования (иногда дублируется Санкт-Петербург и гео возвращает None)
def remove_duplicates(input_string):
    words = input_string.split()  # Разбиваем строку на слова
    seen = set()  # Множество для отслеживания уникальных слов
    result = []

    for word in words:
        if word.replace(",", "") not in seen:
            seen.add(word)
            result.append(word)

    return ' '.join(result)  # Объединяем слова обратно в строку


def to_utc_time(time_str):
    # Преобразование строки в объект datetime
    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

    # Добавляем временную зону UTC
    dt = dt.replace(tzinfo=timezone.utc)

    # Преобразование в формат ISO 8601
    iso_format = dt.isoformat() + "Z"

    return iso_format


def format_datetime(datetime_str):
    # Преобразуем строку в объект datetime
    try:
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%SZ')
    except:
        try:
            dt = datetime.strptime(datetime_str[:-1], '%Y-%m-%dT%H:%M:%S%z')

        except:
            dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
    # Форматируем в нужный вид
    return dt.strftime('%d-%m-%Y %H:%M:%S')


class Parse:
    def __init__(self):
        # Инициализация заголовка для HTTP-запросов
        self.headers = {"accept": "application/json"}

    def get_lot_gos(self, id):
        """
        Получаем данные о лоте по его идентификатору.

        Аргументы:
        - id: Идентификатор лота (str)

        Возвращает словарь с характеристиками лота
        """
        url = f"https://torgi.gov.ru/new/api/public/lotcards/{id}"
        response = requests.get(url=url, headers=self.headers, verify=False)
        res = response.json()

        # Инициализация переменных для площади и кадастрового номера
        square = None
        kadnum = None
        for i in res["characteristics"]:
            if i['name'] == "Общая площадь":
                square = i['characteristicValue']
            if i['name'] == "Кадастровый номер":
                kadnum = i.get("characteristicValue", None)  # Использует метод get для избежания исключений

        # Собирает данные о лоте в словарь
        id = res["id"]
        lot_status = res["lotStatus"]
        price_min = res["priceMin"]
        address = res["estateAddress"]
        bid_end_time = (res["biddEndTime"])
        ref = f'https://torgi.gov.ru/new/public/lots/lot/{id}'
        ph_id = res["lotImages"][0]
        photo_url = f"https://torgi.gov.ru/new/image-preview/v1/{ph_id}?disposition=inline&resize=600x600!"
        lot = {
            "id": id,
            "lot_status": lot_status,
            "price_min": price_min,
            "address": address,
            "bid_end_time": bid_end_time,
            "ref": ref,
            "square": square,
            "kadnum": kadnum,
            "photo_url": photo_url
        }
        return lot

    def get_lots_gos(self):
        res = []

        url = "https://torgi.gov.ru/new/api/public/lotcards/rss?dynSubjRF=79&biddType=&biddForm=&currCode=&chars=&lotStatus=PUBLISHED,APPLICATIONS_SUBMISSION&biddEndFrom=&biddEndTo=&pubFrom=&pubTo=&aucStartFrom=&aucStartTo=&etpCode=&catCode=11&text=&matchPhrase=false&attachmentText=&noticeStatus=&resourceTypeUse=&npa=&typeTransaction=rent&byFirstVersion=true"

        headers = {
            "accept": "application/rss+xml;charset=UTF-8"
        }
        response = requests.get(url, headers, verify=False)

        with open("rss.xml", "w") as file:
            file.write(response.text)

        # Загружаем XML файл
        tree = ET.parse('rss.xml')
        root = tree.getroot()

        def extract_lot_number(url_lot):
            parts = url_lot.split('/')
            return parts[-1]

        # Обрабатываем данные
        for item in root.findall('channel/item'):
            name = item.find('title').text if item.find('title') is not None else 'Нет данных'
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else 'Нет данных'
            guid = item.find('guid').text if item.find('guid') is not None else 'Нет данных'
            res.append(extract_lot_number(guid))

        return res

    def koord(self):
        """
        Получает координаты всех лотов из базы данных и добавляет их в базу.
        """
        for row in lotsbd.cursor.execute("SELECT * FROM lots").fetchall():
            id = row[0]
            address = row[1]
            a = geo.get_free(address)  # Получение координат по адресу
            lotsbd.koord_add(id=id, lon=str(a["longitude"]), lat=str(a["latitude"]))  # Сохранение координат в базе

    def parse_gos(self):
        """
        Парсит данные о лотах из госресурсов и сохраняет их в базе данных.
        """
        for lot_id in self.get_lots_gos():

            lot = self.get_lot_gos(lot_id)
            if lotsbd.check_kad(lot["kadnum"]) is None and lotsbd.check(lot["id"]) is None:
                # Извлечение данных из лота
                address = lot['address']
                lotstatus = lot["lot_status"]
                pricemin = lot["price_min"]
                biddEndTime = format_datetime(lot["bid_end_time"])
                square = lot["square"]
                kadnum = lot["kadnum"]
                ref = lot["ref"]
                photo_url = lot["photo_url"]
                lotsbd.create(lot["id"], address, lotstatus, pricemin, biddEndTime, square, kadnum, ref, photo_url,
                              posted=0)

                ge = geo.get_free(address)
                if ge["longitude"] is None:
                    address_rm = remove_duplicates(address)
                    ge2 = geo.get_free(address_rm)
                    print(address_rm)
                    print(ge2)

                lotsbd.koord_add(lot["id"], lon=str(ge["longitude"]), lat=str(ge["latitude"]))
                time.sleep(1)


parser = Parse()