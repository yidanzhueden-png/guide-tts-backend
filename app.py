import os
import base64
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

        # 截断过长的文本（阿里云限制约 150 字符）
        if len(text) > 150:
            text = text[:150]

        app.logger.info(f"📤 文本: {text[:50]}... 音色: {voice}")

        # 调用 Qwen-TTS（流式模式）
        response = dashscope.MultiModalConversation.call(
            model="qwen3-tts-flash",
            text=text,
            voice=voice,
            language_type="English",
            stream=True  # 关键：流式模式
        )

        # 收集音频数据
        audio_data = b''
        for chunk in response:
            # 兼容不同版本的返回结构
            if hasattr(chunk, 'output') and chunk.output and hasattr(chunk.output, 'audio'):
                audio_data += chunk.output.audio
            elif hasattr(chunk, 'audio'):
                audio_data += chunk.audio
            else:
                # 尝试直接取
                try:
                    audio_data += chunk['output']['audio']
                except (KeyError, TypeError):
                    pass

        if not audio_data:
            app.logger.error("❌ 未接收到音频数据")
            return jsonify({'error': 'No audio data received'}), 500

        # 编码为 base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        app.logger.info(f"✅ 音频生成成功，大小: {len(audio_data)} 字节")

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