
from flask import Flask, request, jsonify, render_template
from serv import content, get_anything, user_option, device, friend, chat

app = Flask(__name__)

app.register_blueprint(content.content_bp)
app.register_blueprint(get_anything.get_any)
app.register_blueprint(user_option.user_bp)
app.register_blueprint(device.dev)
app.register_blueprint(friend.friend_bp)
app.register_blueprint(chat.ch)





@app.route("/")
def index():
    return render_template("index.html")


@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    return response


if __name__ == '__main__':
    app.run("0.0.0.0", 9527, debug=True)
