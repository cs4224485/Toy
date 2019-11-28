from flask import Blueprint, request, jsonify
from settings import MONGO_DB, RET
import pymongo
from bson import ObjectId

dev = Blueprint("dev", __name__)


@dev.route("/dev_QR", methods=["POST"])
def dev_QR():
    '''
    验证二维码是否是玩具二维码
    :return:
    '''

    device_key = request.form.get("device_key")
    scan_type = request.form.get("scan_type")

    res = MONGO_DB.devices.find_one({"device_key": device_key})
    # 1 扫描的不是玩具二维码
    if not res:
        RET["code"] = 1
        RET["msg"] = "请扫描玩具二维码"
        RET["data"] = {}
        return jsonify(RET)

    # 2 user未绑定的玩具开启绑定逻辑 toy 提示玩具未绑定
    RET["code"] = 0
    RET["msg"] = "绑定玩具"
    RET["data"] = {"device_key": device_key, "scan_type": scan_type}

    # 3 已绑定玩具开启添加好友逻辑
    res = MONGO_DB.toys.find_one({"device_key": device_key})  # 被加好友的玩具
    RET["code"] = 1
    RET["msg"] = "添加好友"
    RET["data"] = {"added_toy_id": str(res.get("_id")), "scan_type": scan_type}

    return jsonify(RET)


@dev.route("/bind_toy", methods=["POST"])
def bind_toy():
    '''
    创建玩具的基本信息
    绑定用户与玩具关系
    当前用户成为玩具的第一个好友
    :return:
    '''
    device_key = request.form.get("device_key")
    user_id = request.form.get("user_id")
    toy_name = request.form.get("toy_name")
    baby_name = request.form.get("baby_name")
    remark = request.form.get("remark")
    gender = request.form.get("gender")

    chat_id = MONGO_DB.chat.insert_one({})
    user_info = MONGO_DB.users.find_one({"_id": ObjectId(user_id)})
    toy_info = {
        "device_key": device_key,
        "bind_user": user_id,
        "toy_name": toy_name,
        "avatar": "toy.jpg",
        "baby_name": baby_name,
        "gender": gender,
        # 成为玩具的第一好友
        "friend_list": [
            {"friend_nickname": user_info.get("nickname"),
             "friend_avatar": user_info.get("avatar"),
             "friend_remark": remark,
             "friend_chat": str(chat_id.inserted_id),
             "friend_id": user_id
             }
        ]
    }
    # 创建玩具的基本信息
    toy_id = MONGO_DB.toys.insert_one(toy_info)
    # 玩具和用户聊天记录
    MONGO_DB.chat.update_one({"_id": chat_id.inserted_id},
                             {"$set": {"user_list": [str(toy_id.inserted_id), str(user_info.get("_id"))],
                                       "chat_list": []}})
    # 用户绑定玩具
    user_info["bind_toys"].append(str(toy_id.inserted_id))
    # 用户添加玩具好友
    user_info["friend_list"].append(
        {"friend_nickname": toy_info.get("baby_name"),
         "friend_avatar": toy_info.get("avatar"),
         "friend_remark": toy_info.get("baby_name"),
         "friend_chat": str(chat_id.inserted_id),
         "friend_id": str(toy_id.inserted_id)
         }
    )
    MONGO_DB.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_info})

    RET["code"] = 0
    RET["msg"] = "绑定成功"
    RET["data"] = {}
    return jsonify(RET)


@dev.route("/toy_list", methods=["POST"])
def toy_list():
    user_id = request.form.get("user_id")
    user_info = MONGO_DB.users.find_one({"_id": ObjectId(user_id)})
    bind_toys = user_info.get("bind_toys")
    bind_toys_obj_id = [ObjectId(item) for item in bind_toys]
    toys_list = list(MONGO_DB.toys.find({"_id": {"$in": bind_toys_obj_id}}))  # 返回 pymongo.cursor

    for index, item in enumerate(toys_list):
        toys_list[index]["_id"] = str(item["_id"])
    RET["code"] = 1
    RET["msg"] = "toylist"
    RET["data"] = toys_list
    return jsonify(RET)


@dev.route("/toy_info", methods=["POST"])
def toy_info():
    toy_id = request.form.get("toy_id")
    toy_info = MONGO_DB.toys.find_one({"_id": ObjectId(toy_id)})
    toy_info["_id"] = str(toy_info["_id"])
    RET["code"] = 0
    RET["msg"] = "查询玩具"
    RET["data"] = toy_info

    return jsonify(RET)


@dev.route("/toy_login", methods=["POST"])
def toy_login():
    devicekey = request.form.get("devicekey")
    # 1. 查询玩具是否授权
    res = MONGO_DB.devices.find_one({"device_key": devicekey})
    if not res:
        return jsonify({"audio": "nolience.mp3"})
    if res:
        toy_info = MONGO_DB.toys.find_one({"device_key": devicekey})
        if not toy_info:
            return jsonify({"audio": "Nobind.mp3"})

        if toy_info:
            return jsonify({"audio": "bind.mp3", "toy_id": str(toy_info.get("_id"))})
