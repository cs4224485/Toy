from flask import Blueprint, request, jsonify
from settings import MONGO_DB, RET
import pymongo
from bson import ObjectId

user_bp = Blueprint("user_bp", __name__)


@user_bp.route("/reg", methods=["POST"])
def reg():
    username = request.form.get("username")
    password = request.form.get("password")
    nickname = request.form.get("nickname")
    phone = request.form.get("phone")
    gender = request.form.get("gender")

    user_info = {
        "username": username,
        "password": password,
        "nickname": nickname,
        "phone": phone,
        "gender": gender,
        "bind_toys": [],
        "friend_list": []
    }

    res = MONGO_DB.users.insert_one(user_info)
    RET["msg"] = "注册成功"
    RET["DATA"] = {"user_id": str(res.inserted_id)}
    return jsonify(RET)


@user_bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    res = MONGO_DB.users.find_one({"username": username, "password": password}, {"password": 0})
    print(res)
    if not res:
        RET["msg"] = "用户不存在"
        RET["code"] = 1
        return jsonify(RET)

    res["_id"] = str(res["_id"])

    RET["code"] = 0
    RET["msg"] = "用户信息"
    RET["data"] = res

    return jsonify(RET)


@user_bp.route("/get_user_info", methods=["POST"])
def get_user_info():
    user_id = request.form.get("user_id")
    res = MONGO_DB.users.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    res["_id"] = str(res["_id"])
    RET["code"] = 0
    RET["msg"] = "用户信息"
    RET["data"] = res

    return jsonify(RET)


