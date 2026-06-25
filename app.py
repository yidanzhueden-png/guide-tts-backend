import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 从环境变量读取 API Key
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "").strip()
TTS_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        text = data.get('text', '').strip()
        voice = data.get('voice', 'Cherry').strip()

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if not DASHSCOPE_API_KEY:
            return jsonify({'error': 'DASHSCOPE_API_KEY not set'}), 500

        headers = {
            'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": "qwen3-tts-flash",
            "input": {
                "text": text,
                "voice": voice,
                "language_type": "English"
            }
        }

        response = requests.post(TTS_URL, headers=headers, json=payload, timeout=30)
        result = response.json()

        if response.status_code != 200:
            error_msg = result.get('message', 'Unknown error')
            return jsonify({'error': f'API error: {error_msg}'}), 500

        audio_url = result.get('output', {}).get('audio', {}).get('url')
        if not audio_url:
            return jsonify({'error': 'No audio URL returned'}), 500

        return jsonify({'audio_url': audio_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)