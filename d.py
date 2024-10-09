import requests


def get_map_urt(latitude, longitude, api_map):
    api = "bfb6d087-79d4-406f-ae25-c704ef5bc87b"
    url_map = f'''https://static-maps.yandex.ru/v1?ll={latitude},{longitude}&size=600,450&z=13&pt={latitude},{longitude}&apikey=bfb6d087-79d4-406f-ae25-c704ef5bc87b'''
    return url_map

