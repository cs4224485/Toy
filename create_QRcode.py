import requests
from uuid import uuid4
import time
import os
import hashlib
from settings import QR_URL, MONGO_DB, QRCODE_PATH

qr_text_list = []
for i in range(5):
    qr_text = hashlib.md5(f"{uuid4()}{time.time()}{uuid4()}".encode("utf-8")).hexdigest()
    res = requests.get(url=QR_URL % (qr_text))
    qr_path = os.path.join(QRCODE_PATH, qr_text)
    with open(f"{qr_path}.jpg", "wb")as f:
        f.write(res.content)
    device_dict = {"device_key": qr_text}
    qr_text_list.append(device_dict)
MONGO_DB.devices.insert_many(qr_text_list)
