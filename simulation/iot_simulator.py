import random
import requests
import time

URL = "http://127.0.0.1:5000/detect"

while True:
    devices = []

    for i in range(5):
        if random.random() < 0.2:
            req = random.randint(500, 1500)  # attack
        else:
            req = random.randint(10, 50)     # normal

        devices.append({
            "device_id": f"device_{i+1}",
            "requests": req
        })

    print("Sending:", devices)

    res = requests.post(URL, json=devices)
    print("Response:", res.json())

    time.sleep(3)