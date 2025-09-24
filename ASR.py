import os
import json
import requests
import LLMmain

BASE = os.getenv("QINIU_BASE_URL", "https://openai.qiniu.com/v1")
API_KEY = os.getenv("QINIU_TTS_KEY", LLMmain.openai_api_key)  # 建议用环境变量
AUDIO_URL = os.getenv(
    "ASR_AUDIO_URL",
    "https://static.qiniu.com/ai-inference/example-resources/example.mp3"  # 官方示例URL
)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",   # 文档要求 Bearer 前缀
}

payload = {
    "model": "asr",
    "audio": {
        "format": "mp3",
        "url": AUDIO_URL            # 必须是 http(s) 公网可访问
    }
}

resp = requests.post(f"{BASE}/voice/asr", headers=headers, json=payload, timeout=60)
print("HTTP", resp.status_code)
print("Body (preview):", resp.text[:500])

resp.raise_for_status()
data = resp.json()
# 返回结构：data.result.text
text = (data.get("data", {}).get("result", {}) or {}).get("text")
print("\n识别文本：", text or "<未返回文本>")
