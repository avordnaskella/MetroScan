import paho.mqtt.client as mqtt
import time
import random
import requests

# Настройки MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Эмулируем антенну, отправляющую HTTP-запросы напрямую на Django
DJANGO_URL = "http://127.0.0.1:8000/api/register_pass/"

# Тестовые данные (должны совпадать с БД)
TRAINS = {
    "RFID_001": "27026",   # поезд с маршрутом 27026
    "RFID_002": "115",     # поезд с маршрутом 115
    "RFID_003": "5",       # поезд с маршрутом 5
    "RFID_004": "2",       # поезд с маршрутом 2
    "RFID_000006": "8997", # ложный
    "RFID_000009": "938487383", # ложный

}

STATIONS = ["Стрелка", "Волжская набережная", "Оперный театр"]

def send_pass():
    tag_id = random.choice(list(TRAINS.keys()))
    station = random.choice(STATIONS)
    
    data = {
        "tag_id": tag_id,
        "station": station
    }
    
    print(f"Отправка: tag_id={tag_id}, станция={station}")
    
    try:
        response = requests.post(DJANGO_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"Поезд {result.get('route_number', '???')} прибыл!")
        else:
            print(f"Ошибка: {response.json().get('message', 'Неизвестная метка')}")
    except Exception as e:
        print(f"Ошибка подключения: {e}")

if __name__ == "__main__":
    print("Эмулятор RFID-антенны запущен (нажмите Ctrl+C для остановки)")
    print(f"Отправка данных на {DJANGO_URL}")
    print("=" * 50)
    
    try:
        while True:
            send_pass()
            time.sleep(10)  # Каждые 10 секунд
    except KeyboardInterrupt:
        print("\nЭмулятор остановлен")