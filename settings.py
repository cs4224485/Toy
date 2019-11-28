import pymongo
import os
import redis

# 数据库配置
mongo_client = pymongo.MongoClient(host="127.0.0.1", port=27017)
MONGO_DB = mongo_client['IntelligentToy']
REDIS_POOL = redis.ConnectionPool(host='10.211.55.4', port=6379)
REDIS_CONN = redis.Redis(connection_pool=REDIS_POOL)

# 数据采集配置
XPP_URL = "https://m.ximalaya.com/tracks/%s.json"

# 资源路径配置
IMAGE_PATH = "Images"
MUSIC_PATH = "Music"
QRCODE_PATH = "QRcode"
CHAT_PATH = "chat"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
}

# 协议格式：
RET = {
    "code": 0,
    "msg": "",
    "data": {}
}
# 创建二维码
QR_URL = "http://qr.topscan.com/api.php?text=%s"

# 百度AI配置
from aip import AipSpeech, AipNlp

""" 你的 APPID AK SK """
APP_ID = '16492489'
API_KEY = 'OtRCgIroimxFzzRiSGn6aYpF'
SECRET_KEY = 'VFUBtnQCIkq6nRcKElZ8wtK8La4R7mtC'
SPEECH = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
NLP = AipNlp(APP_ID, API_KEY, SECRET_KEY)

# 图灵机器人配置:
TULING_URL = "http://openapi.tuling123.com/openapi/api/v2"
