from flask import Blueprint, request, send_file, jsonify
from settings import MONGO_DB, IMAGE_PATH, MUSIC_PATH, CHAT_PATH, RET, REDIS_CONN
import os, json
from baidu_aip.baidu_asr_sync import text2audio

ch = Blueprint("ch", __name__)


@ch.route("/open_chat", methods=["POST"])
def open_chat():
    user_id = request.form.get("user_id")
    friend_id = request.form.get("friend_id")
    chat_window = MONGO_DB.chat.find_one({"user_list": {"$all": [user_id, friend_id]}})
    chat_window["_id"] = str(chat_window["_id"])
    RET["code"] = 0
    RET["msg"] = "聊天窗口"
    RET["data"] = chat_window
    clear_msg(friend_id, user_id)
    return jsonify(RET)


@ch.route("/recv_msg", methods=["POST"])
def recv_msg():
    '''
    玩具端收取消息
    :return:
    '''
    sender = request.form.get("sender")
    to_user = request.form.get("to_user")

    msg_count = get_redis_count(sender, to_user)
    if msg_count:
        chat_window = MONGO_DB.chat.find_one({"user_list": {"$all": [sender, to_user]}})
    else:
        sender, msg_count = get_redis_random(to_user)
        if not sender:
            filename = text2audio("没有未读消息了, 别再按了")
            return jsonify([{"msg": filename}])
        chat_window = MONGO_DB.chat.find_one({"user_list": {"$all": [sender, to_user]}})
    msg_list = []
    for chat in reversed(chat_window["chat_list"]):
        if len(msg_list) == msg_count:
            break
        if chat.get("sender") == sender:
            msg_list.append(chat_window)
    msg_list.reverse()
    clear_msg(sender, to_user)
    return jsonify(msg_list)


@ch.route("/user_msg", methods=["POST"])
def user_msg():
    '''
    获取离线消息
    :return:
    '''
    user_id = request.form.get("user_id")
    msg = get_redis(user_id)
    RET["code"] = 0
    RET["msg"] = "查询未读消息"
    RET["data"] = msg
    return jsonify(RET)


def get_redis_count(sender, to_user):
    msg = REDIS_CONN.get(to_user)
    if msg:
        msg = json.loads(msg)
        return msg[sender]


def get_redis(to_user):
    msg = REDIS_CONN.get(to_user)
    if msg:
        msg = json.loads(msg)
        msg["count"] = sum(msg.values())
        return


def clear_msg(sender, to_user):
    msg = REDIS_CONN.get(to_user)
    if msg:
        msg = json.loads(msg)
        msg[sender] = 0

    REDIS_CONN.set(to_user, json.dumps(msg))


def get_redis_random(toy_id):
    '''
    随机读取离线消息
    :param toy_id:
    :return:
    '''
    toy_msg = REDIS_CONN.get(toy_id)
    if toy_msg:
        toy_msg = json.loads(toy_msg)
        for sender, count in toy_msg.items():
            if count:
                return sender, count
    return None, None
