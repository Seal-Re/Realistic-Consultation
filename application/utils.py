import re
import os
import logging
import subprocess
from pymongo import MongoClient
from .MongoBase import mongo_url, DBbase

client = None

def connect_to_mongodb():
    global client
    try:
        client = MongoClient(mongo_url)
        logging.debug("Connected to MongoDB successfully")
        return client
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        return None

def close_mongodb_connection():
    global client
    if client:
        client.close()
        logging.debug("MongoDB connection closed")

def read_mongo_data(collection):
    try:
        data = list(collection.find({}, {"_id": 0}))
        logging.debug(f"Read {len(data)} documents from collection {collection.name}")
        return data if data else []
    except Exception as e:
        logging.error(f"Error reading from MongoDB collection {collection.name}: {e}")
        return []


voiceMap = {
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
    "yunjian": "zh-CN-YunjianNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "yunxia": "zh-CN-YunxiaNeural",
    "yunyang": "zh-CN-YunyangNeural",
    "xiaobei": "zh-CN-liaoning-XiaobeiNeural",
    "xiaoni": "zh-CN-shaanxi-XiaoniNeural",
    "hiugaai": "zh-HK-HiuGaaiNeural",
    "hiumaan": "zh-HK-HiuMaanNeural",
    "wanlung": "zh-HK-WanLungNeural",
    "hsiaochen": "zh-TW-HsiaoChenNeural",
    "hsioayu": "zh-TW-HsiaoYuNeural",
    "yunjhe": "zh-TW-YunJheNeural",
}

def getVoiceById(voiceId):
    return voiceMap.get(voiceId)

def remove_html(string):
    return re.sub(r'<[^>]+>', '', string)

def createAudio(text, file_name, voiceId):
    new_text = remove_html(text)
    voice = getVoiceById(voiceId)
    if not voice:
        return "error params"

    file_path = os.path.join(os.getcwd(), "tts", file_name)
    relative_path = "/tts/" + file_name
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        subprocess.run(
            ['edge-tts', '--voice', voice, '--text', new_text, '--write-media', file_path],
            check=True
        )
        return f'http://127.0.0.1:2020{relative_path}'
    except subprocess.CalledProcessError as e:
        logging.error(f"创建音频失败: {e}")
        return "创建音频失败"
    except Exception as e:
        logging.error(f"处理音频时发生其他错误: {e}")
        return "处理音频时发生错误"

def getParameter(request, paramName):
    return request.args.get(paramName, "")

connect_to_mongodb()
if client:
    db = client[DBbase]
    ai_history = db["ai_history"]
    table_pool = db["TablePool"]
