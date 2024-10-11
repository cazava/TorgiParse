import requests
import config

#Получение координат по адресу

url = "https://geocode.gate.petersburg.ru"
headers = {
    "accept": "application/json",
    "Authorization": f'Bearer {config.token_geo}'
}
free = "/parse/free"


def get_free(address):
    path = url + free

    params = {
        "street": address
    }

    response = requests.get(path, headers=headers, params=params)
    res = response.json()
    try:
        longitude = res["Longitude"]
        latitude = res["Latitude"]
    except:
        longitude = None
        latitude = None
    return {
        "longitude": longitude,
        "latitude": latitude
    }