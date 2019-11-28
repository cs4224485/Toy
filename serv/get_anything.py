from flask import Blueprint, request, send_file, jsonify
from settings import MONGO_DB, IMAGE_PATH, MUSIC_PATH, CHAT_PATH, RET
import os
from bson import ObjectId
from uuid import uuid4
from baidu_aip.baidu_asr_sync import audio2text, my_nlp_lowb

get_any = Blueprint("get_any", __name__)


@get_any.route("/get_music/<filename>")
def get_music(filename):
    filename = os.path.join(MUSIC_PATH, filename)
    return send_file(filename)


@get_any.route("/get_chat/<filename>")
def get_chat(filename):
    filename = os.path.join(CHAT_PATH, filename)
    return send_file(filename)


@get_any.route("/get_image/<filename>")
def get_image(filename):
    filename = os.path.join(IMAGE_PATH, filename)
    return send_file(filename)


@get_any.route("/uploder", methods=["POST"])
def uploder():
    '''
    上传和保存聊天记录
    :return:
    '''
    record_file = request.files.get("record")
    chat_window = request.form.get("chat_window")
    user_id = request.form.get("user_id")
    record_path = os.path.join(CHAT_PATH, record_file.filename)
    record_file.save(record_path)
    os.system(f"ffmpeg  -i {record_path}  {record_path}.mp3")
    # chat = MONGO_DB.chat.findo_one({"_id": ObjectId(chat_window)})
    sender_msg = {
        "sender": user_id,
        "msg": record_file.filename + ".mp3"
    }
    MONGO_DB.chat.update_one({"_id": ObjectId(chat_window)}, {"$push": {"chat_list": sender_msg}})
    RET["code"] = 0
    RET["msg"] = ""
    RET["data"] = {}

    return jsonify(RET)


@get_any.route("/toy_ai", methods=["POST"])
def toy_ai():
    '''
    语言AI点播
    :return:
    '''
    file_name = f"{uuid4()}.wav"
    record_file = request.files.get("record")
    sender = request.form.get("sender")
    # to_user = request.form.get('to_user')
    record_path = os.path.join(CHAT_PATH, file_name)
    record_file.save(record_path)
    text = audio2text(record_path)
    print(text)
    ret_dict = my_nlp_lowb(text, sender)
    return jsonify(ret_dict)
