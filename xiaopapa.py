import requests
from settings import MONGO_DB, IMAGE_PATH, MUSIC_PATH, headers, XPP_URL
from uuid import uuid4
import os

target_url = "/ertong/424529/7713546"
target_id = target_url.split("/")[-1]

target_url = XPP_URL % target_id
res = requests.get(target_url, headers=headers)
data_type = "erge"
data_name = str(uuid4())
data_music_path = os.path.join(MUSIC_PATH, data_name)
data_image_path = os.path.join(IMAGE_PATH, data_name)
content_info = res.json()
audio = requests.get(content_info.get("play_path_64"))
image = requests.get(content_info.get("cover_url"))

with open(f"{data_music_path}.mp3", "wb") as f:
    f.write(audio.content)

with open(f"{data_image_path}.jpg", "wb") as f:
    f.write(image.content)

title = content_info.get("title")
nickname = content_info.get('nickname')
album_title = content_info.get('album_title')
intro = content_info.get('intro')
play_count = 0

content = {
    "title": title,
    "nickname": nickname,
    "album_title": album_title,
    "intro": intro,
    "play_count": play_count,
    "data_type": data_type,
    "audio": f"{data_name}.mp3",
    "image": f"{data_name}.jpg"
}

MONGO_DB.content.insert_one(content)

