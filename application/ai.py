from flask import Blueprint, jsonify, request
from openai import OpenAI
import logging
from .AIBase import api_key, base_url
from .utils import ai_history

ai_bp = Blueprint('ai', __name__)
client = OpenAI(api_key=api_key, base_url=base_url)

preset_prompt = "我想让你扮演虚拟医生。我是一名不懂医学的普通病人。我会描述我的症状，你会提供诊断和治疗方案。只回复你的诊疗方案，其他不回复。你的回答应该平易近人，并且显示对病人的友好。不要写解释。换行请用'\\n'使用utf-8编码，不要用markdown语法。"

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('error.log', encoding='utf-8')
    ]
)

MAX_HISTORY_LENGTH = 10


@ai_bp.route('/api/AI', methods=['POST'])
def get_ai_response():
    try:
        data = request.get_json()
        user_question = data.get('question')
        session_id = data.get('session_id')

        if not user_question:
            return jsonify({"message": "Missing question parameter"}), 400

        if session_id is not None:
            record = ai_history.find_one({"session_id": session_id})
        else:
            record = ai_history.find_one(sort=[("session_id", -1)])

        if record:
            session_id = record["session_id"]
            messages = record.get("history", [])
        else:
            session_id = 1
            messages = []

        if not messages or messages[0].get("role") != "system":
            messages.insert(0, {"role": "system", "content": preset_prompt})

        if messages[-1]["role"] == "user":
            messages[-1]["content"] = user_question
        else:
            messages.append({"role": "user", "content": user_question})

        # Trim: keep under MAX_HISTORY_LENGTH, ensure index 1 is always a user message
        while len(messages) > 1 and (len(messages) > MAX_HISTORY_LENGTH or messages[1]["role"] == "assistant"):
            messages.pop(1)

        for msg in messages:
            msg.pop("reasoning_content", None)

        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages
        )

        ai_answer = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_answer})

        ai_history.update_one(
            {"session_id": session_id},
            {"$set": {"history": messages}},
            upsert=True
        )

        return jsonify({"message": ai_answer})

    except Exception as e:
        logging.error(f"Error in get_ai_response: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500


@ai_bp.route('/api/AI_new', methods=['POST'])
def create_new_ai_session():
    try:
        last_record = ai_history.find_one(sort=[("session_id", -1)])
        new_session_id = last_record["session_id"] + 1 if last_record else 1

        ai_history.insert_one({
            "session_id": new_session_id,
            "history": []
        })

        return jsonify({
            "message": "New AI session created",
            "session_id": new_session_id
        })

    except Exception as e:
        logging.error(f"Error creating new AI session: {e}")
        return jsonify({"message": f"Error: {str(e)}"}), 500


@ai_bp.route('/api/content', methods=['GET'])
def get_chat_history():
    session_id = request.args.get('session_id', type=int)

    if session_id is not None:
        latest_session = ai_history.find_one({"session_id": session_id})
    else:
        latest_session = ai_history.find_one(sort=[("session_id", -1)])

    if not latest_session:
        return jsonify({"message": "无会话记录", "data": []}), 200

    chat_history = latest_session.get("history", [])

    if chat_history and chat_history[0].get("role") == "system":
        chat_history = chat_history[1:]

    formatted = [
        {"role": msg.get("role", ""), "content": msg.get("content", "")}
        for msg in chat_history
    ]

    return jsonify({"message": "获取成功", "data": formatted}), 200
