import os
import base64
import requests
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import dashscope

app = Flask(__name__)
CORS(app)

# 从环境变量读取 API Key
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "sk-ws-H.RYHIXYM.paeH.MEYCIQC2ym6R-fNET3EahbfhvqLByoOYEmhuCb8cL5sh-fwpWgIhAMQCcOMNF9ID0XNiA4w1_O9NnzrsJj0fKL4NEwTM0MAo").strip()
if not DASHSCOPE_API_KEY:
    app.logger.warning("⚠️ DASHSCOPE_API_KEY 未设置")

# 设置 dashscope 配置
dashscope.api_key = DASHSCOPE_API_KEY
dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

@app.route('/tts', methods=['POST'])
def text_to_speech():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        text = data.get('text', '').strip()
        voice = data.get('voice', 'Serena').strip()

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if not DASHSCOPE_API_KEY:
            app.logger.error("DASHSCOPE_API_KEY 未设置")
            return jsonify({'error': 'Server configuration error'}), 500

        # 截断过长文本
        if len(text) > 150:
            text = text[:150]

        app.logger.info(f"📤 文本: {text[:50]}... 音色: {voice}")

        # 非流式调用，获取音频 URL
        response = dashscope.MultiModalConversation.call(
            model="qwen3-tts-flash",
            text=text,
            voice=voice,
            language_type="English",
            stream=False  # 非流式
        )

        # 提取音频 URL
        audio_url = response.output.audio.url
        if not audio_url:
            app.logger.error("❌ 未获取到音频 URL")
            return jsonify({'error': 'No audio URL returned'}), 500

        app.logger.info(f"✅ 获取音频 URL: {audio_url}")

        # 从 OSS 下载音频二进制数据（后端下载，避免跨域）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://dashscope.aliyuncs.com/'
        }
        audio_resp = requests.get(audio_url, headers=headers, timeout=30)
        if audio_resp.status_code != 200:
            app.logger.error(f"❌ 下载音频失败: {audio_resp.status_code}")
            return jsonify({'error': 'Failed to download audio'}), 500

        audio_data = audio_resp.content
        # 编码为 base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        app.logger.info(f"✅ 音频下载成功，大小: {len(audio_data)} 字节")

        return jsonify({
            'audio_base64': audio_base64,
            'format': 'wav'
        })

    except Exception as e:
        app.logger.error(f"❌ 内部错误: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)