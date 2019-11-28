from flask import Flask, request
from geventwebsocket.websocket import WebSocket
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import json
from baidu_aip.baidu_asr_sync import text2audio
from settings import MONGO_DB, REDIS_CONN
from bson import ObjectId

websocket_app = Flask(__name__)
user_socket_dict = {}


@websocket_app.route("/ws/<uid>")
def ws(uid):
    print(request.method)
    user_socket = request.environ.get("wsgi.websocket")  # type:WebSocket
    user_socket_dict[uid] = user_socket
    print(len(user_socket_dict), user_socket_dict)
    while True:
        try:
            msg = user_socket.receive()
            print(msg, 'msg')
            msg_dict = json.loads(msg)  # {to_user:132,  music:abc.mp3}
            to_user = msg_dict.get("to_user")

            to_user_socket = user_socket_dict.get(to_user)
            send_something = {}
            msg = send_msg(uid, to_user)
            if msg_dict.get("chat"):
                send_something = {"msg_type": "chat", "msg": msg, "from_user": uid}
                set_redis(uid, to_user)
            if msg_dict.get("music"):
                send_something = {"msg_type": "music", "msg": msg_dict.get("music")}

            if to_user_socket:
                to_user_socket.send(json.dumps(send_something))

        except Exception as e:
            continue


@websocket_app.route("/tow_ws/<uid>")
def toy(uid):
    '''
    玩具向app发消息
    :param uid:
    :return:
    '''
    user_socket = request.environ.get("wsgi.websocket")
    user_socket_dict[uid] = user_socket
    while True:
        msg = user_socket.receive()
        msg_dict = json.loads(msg)
        to_user = msg_dict.get("to_user")
        user = MONGO_DB.users.find({"_id": ObjectId(to_user)})
        if user:
            user_type = "user"
        else:
            user_type = "toy"
        to_user_socket = user_socket.get(to_user)

        if to_user_socket:
            # 给用户APP发消息
            if user_type == "user":
                send_str = json.dumps({"sender": uid})
                set_redis(uid, to_user)
                to_user_socket.send(send_str)
            # 给玩具用户发消息
            else:
                msg = send_msg(uid, to_user)
                set_redis(uid, to_user)
                send_something = {"msg_type": "chat", "msg": msg, "from_user": uid}
                to_user_socket.send(json.dumps(send_something))


def set_redis(sender, to_user):
    '''
    将离线消息存入redis
    :param sender:
    :param to_user:
    :return:
    '''
    user_msg = REDIS_CONN.get(to_user)
    # 如果收消息的人当前消息是空值 则创建一条数据
    if not user_msg:
        REDIS_CONN.set(to_user, json.dumps({sender: 1}))
    else:
        user_msg = json.loads(user_msg)
        # 如果收消息的对象存在但是里面没有当前发送者的消息则创建
        if not user_msg.get(sender):
            user_msg[sender] = 1
        # 如果存在当前发送者则使当前消息+1
        else:
            user_msg[sender] += 1
        REDIS_CONN.set(to_user, json.dumps(user_msg))


def send_msg(sender, to_user):
    '''
    获取称呼
    :param sender:发送消息的用户
    :param to_user:接收消息的用户(一定是玩具)
    :return:
    '''
    to_user_info = MONGO_DB.toys.find_one({"_id": ObjectId(to_user)})
    for friend in to_user_info.get("friend_list"):
        if friend.get("friend_id") == sender:
            remark = friend.get("friend_remark")
            msg = text2audio(f"你有来自{remark}消息")
            return msg


if __name__ == '__main__':
    http_serv = WSGIServer(("0.0.0.0", 9521), websocket_app, handler_class=WebSocketHandler)
    http_serv.serve_forever()
