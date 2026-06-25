import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 从环境变量读取 API Key（更安全）
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-ws-H.RYHIXYM.paeH.MEYCIQC2ym6R-fNET3EahbfhvqLByoOYEmhuCb8cL5sh-fwpWgIhAMQCcOMNF9ID0XNiA4w1_O9NnzrsJj0fKL4NEwTM0MAo").strip()
TTS_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

@app.route('/tts', methods=['POST'])
def text_to_speech():
    # ... 你的原有代码保持不变 ...
    pass

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

# 生产环境不在这里启动
# if __name__ == '__main__':
#     app.run(debug=True, port=5000)