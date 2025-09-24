import requests
import LLMmain
import base64
import pygame
import tempfile
import time

def TTS(content):
    url = "https://openai.qiniu.com/v1/voice/tts"
    headers = {
        "Content-Type": "application/json",
        "Authorization": LLMmain.openai_api_key
    }

    data = {
        "audio": {
            "voice_type": "qiniu_zh_female_tmjxxy",
            "encoding": "mp3",
            "speed_ratio": 1.0
        },
        "request": {
            "text": content
        }
    }

    response = requests.post(url, headers=headers, json=data)
    return response


def smart_play_audio(base64_string):
    """智能检测音频格式并播放"""
    # 解码Base64
    audio_data = base64.b64decode(base64_string)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
        f.write(audio_data)
        temp_file = f.name

    # 播放音频
    print("开始播放音频...")
    pygame.mixer.init()
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)
    print("音频播放完成")
# response = TTS(LLMmain.fristsentence)
# data_json = response.json()
# data_content = data_json['data']
# smart_play_audio(data_content)

