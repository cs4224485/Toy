from settings import SPEECH, CHAT_PATH, MONGO_DB, TULING_URL
from uuid import uuid4
from bson import ObjectId
import os, requests, json
import jieba
import gensim
from gensim import corpora
from gensim import models
from gensim import similarities


def text2audio(text):
    filename = f"{uuid4()}.mp3"
    file_path = os.path.join(CHAT_PATH, filename)
    res = SPEECH.synthesis(text, options={
        "vol": 8,
        "plt": 8,
        "spd": 5,
        "per": 4
    })

    with open(file_path, "wb") as f:
        f.write(res)
    return filename


def audio2text(filename):
    res = SPEECH.asr(speech=get_file_content(filename), options={"dev_pid": 1536, })
    return res.get("result")[0]


def get_file_content(filePath):
    cmd_str = f"ffmpeg -y  -i {filePath}  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 {filePath}.pcm"
    os.system(cmd_str)
    with open(f"{filePath}.pcm", "rb") as fp:
        return fp.read()


def my_nlp_lowb(Q, uid=None):
    ret_dict = {
        "music": "",
        "type": "",
        "to_user": ""
    }
    if "我要听" in Q or "我想听" in Q:
        title, score = my_yuliaoku(Q)
        if score > 0:
            audio = MONGO_DB.content.find_one({"title":title})
            ret_dict["music"] = audio.get("audio")
            ret_dict["type"] = "music"
            return ret_dict

    if "发消息" in Q or "聊聊天" in Q or "说说话" in Q:
        toy_info = MONGO_DB.toys.find_one({"_id": ObjectId(uid)})
        for friend in toy_info.get("friend_list"):
            if friend.get("friend_remark") in Q or friend.get("friend_nickname") in Q:
                filename = text2audio(f"可以按消息建, 给{friend.get('friend_remark')}发消息了")
                ret_dict["music"] = filename
                ret_dict["type"] = "chat"
                ret_dict["to_user"] = friend.get("friend_id")
                return filename, "chat"
    ret_dict["music"] = text2audio(go_to_tuling(Q, uid))
    ret_dict["type"] = "chat"
    return ret_dict


def go_to_tuling(question_text, uid):
    tuling_url = "http://openapi.tuling123.com/openapi/api/v2"
    to_tuling_str = {
        "reqType": 0,
        "perception": {
            "inputText": {
                "text": question_text
            },
            "inputImage": {
                "url": "imageUrl"
            },
        },
        "userInfo": {
            "apiKey": "ce49eafcd3c449b7bd8379c5c8b2ca21",
            "userId": uid
        }
    }
    a = requests.post(url=tuling_url, json=to_tuling_str)

    res = json.loads(a.text)
    return res.get("results")[0]["values"]["text"]


# 语料库
l1 = [content.get("title") for content in MONGO_DB.content.find({})]
all_doc_list = []
for doc in l1:
    # 分词
    doc_list = [word for word in jieba.cut(doc)]
    all_doc_list.append(doc_list)
# 制作词袋
dictionary = corpora.Dictionary(all_doc_list)
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
lsi = models.LsiModel(corpus)
index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))


def my_yuliaoku(a):
    # 对用户输入的句子分词
    doc_test_list = [word for word in jieba.cut(a)]
    doc_test_vec = dictionary.doc2bow(doc_test_list)
    sim = index[lsi[doc_test_vec]]

    cc = sorted(enumerate(sim), key=lambda item: -item[1])
    text = l1[cc[0][0]]
    return text, cc[0][1]
