import urllib3

import requests
import xml.etree.ElementTree as ET
from bd import lotsbd
import geocoder as geo
from datetime import datetime, timezone

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        Получает данные о лоте по его идентификатору.

        Аргументы:
        - id: Идентификатор лота (str)

        Возвращает словарь с характеристиками лота или None в случае ошибки.
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

    # def get_lots_fond(self, page: int):
    #     """
    #     Получает лоты из фонда по указанной странице.
    #
    #     Аргументы:
    #     - page: Номер страницы (int)
    #
    #     Возвращает список лотов или None в случае ошибки.
    #     """
    #     ur = f"https://xn--80adfeoyeh6akig5e.xn--p1ai/v1/items?areaMax=6200070&page={page}&pagination=%7B%22page%22:%222%22,%22perPage%22:21,%22totalPages%22:0%7D&per-page=21&sort=-dateBid&statusId=2&typeId=0"
    #     headers = {"accept": "application/json"}
    #
    #     payload = {
    #         "areaMax": 6200070,
    #         "page": page,
    #         "pagination": {"page": f"{page}", "perPage": 200, "totalPages": 0},
    #         "per-page": 200,
    #         "sort": "-dateBid",
    #         "statusId": 2,
    #         "typeId": 0
    #     }
    #     response = requests.get(ur, headers=headers, params=payload, verify=False)
    #     data = response.json()
    #     return data["items"]  # Возвращает список лотов из фонда

    # def get_lot_fond(self, lot):
    #     """
    #     Получает данные о конкретном лоте из фонда.
    #
    #     Аргументы:
    #     - lot: Словарь с данными о лоте
    #
    #     Возвращает словарь с характеристиками лота или None, если категория не соответствует.
    #     """
    #     res = {}
    #     if lot["categoryId"] == 1 or lot["categoryId"] == 2:
    #         res["kadnum"] = lot["catastralNumber"]
    #         res["bidendtime"] = format_datetime(lot["dateClose"])
    #         res["address"] = lot["address"]
    #         res["id"] = lot["id"]
    #         res["square"] = lot["totalArea"]
    #         res["pricemin"] = lot["startingPrice"]
    #         res["latitude"] = lot["latitude"]
    #         res["longitude"] = lot["longitude"]
    #         res["ref"] = f'https://xn--80adfeoyeh6akig5e.xn--p1ai/realty/spaces/' + str(lot["id"])
    #         res["lotstatus"] = "APPLICATIONS_SUBMISSION"
    #         res["photo_url"] = None
    #         return res  # Возвращает данные о лоте, если категория соответствует, иначе None
    #     else:
    #         return None

    def koord(self):
        """
        Получает координаты всех лотов из базы данных и добавляет их в базу.
        """
        for row in lotsbd.cursor.execute("SELECT * FROM lots").fetchall():
            id = row[0]
            address = row[1]
            a = geo.get_free(address)  # Получение координат по адресу
            lotsbd.koord_add(id=id, lon=a["longitude"], lat=a["latitude"])  # Сохранение координат в базе

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
                lotsbd.koord_add(lot["id"], lon=ge["longitude"], lat=ge["latitude"])

    # def parse_fond(self):
    #     """
    #     Парсит данные о лотах из госресурсов и сохраняет их в базе данных.
    #     """
    #     for page in range(1, 4):
    #         lots = self.get_lots_fond(page)
    #         for lot in lots:
    #             kadnum = lot["catastralNumber"]
    #
    #             if (kadnum) is None:
    #                 continue  # Если идентификатор пуст, выходим из цикла
    #             if lotsbd.check_kad(kadnum) is None and self.get_lot_fond(
    #                     lot) is not None:  # Проверка, существует ли лот в базе
    #                 l = self.get_lot_fond(lot)
    #                 # Извлечение данных из лота
    #                 biddEndTime = lot["dateClose"]
    #                 if datetime.strptime(biddEndTime, "%Y-%m-%d %H:%M:%S") < datetime.now():
    #                     continue
    #                 id = l["id"]
    #                 address = l['address']
    #                 lotstatus = "APPLICATIONS_SUBMISSION"
    #                 pricemin = l["pricemin"]
    #
    #                 square = l["square"]
    #                 kadnum = l["kadnum"]
    #                 ref = l["ref"]
    #                 longitude = l["longitude"]
    #                 latitude = l["latitude"]
    #                 photo_url = l["photo_url"]
    #
    #                 # Сохранение нового лота в базе данных
    #                 lotsbd.create(id, address, lotstatus, pricemin, biddEndTime, square, kadnum, ref, photo_url,
    #                               posted=0)
    #                 lotsbd.koord_add(id, longitude, latitude)
    #             else:
    #                 continue  # Если лот уже в базе, переходим к следующему


parser = Parse()
