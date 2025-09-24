import os
import LLMmain
import pyaudio
import io
import wave
import base64
import requests
import datetime

# 音频录制参数
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # 16kHz采样率，适合语音识别
RECORD_SECONDS = 5  # 录制5秒


def list_audio_devices():
    """列出所有可用的音频设备"""
    p = pyaudio.PyAudio()
    print("可用的音频设备:")
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        print(f"设备 {i}: {device_info['name']}")
        print(f"   最大输入通道数: {device_info['maxInputChannels']}")
        print(f"   最大输出通道数: {device_info['maxOutputChannels']}")
    p.terminate()


def find_input_device():
    """查找可用的输入设备"""
    p = pyaudio.PyAudio()
    input_device = None

    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f"找到输入设备: {i} - {device_info['name']}")
            input_device = i
            break

    p.terminate()
    return input_device


def record_audio():
    """录制麦克风音频并返回base64编码的音频数据"""
    try:
        p = pyaudio.PyAudio()

        # 查找可用的输入设备
        input_device = find_input_device()
        if input_device is None:
            print("错误: 未找到可用的音频输入设备")
            list_audio_devices()
            return None

        print(f"使用音频输入设备: {input_device}")
        print("开始录音...（5秒）")

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=input_device,  # 指定输入设备
                        frames_per_buffer=CHUNK)

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("录音结束")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # 将音频数据转换为WAV格式的base64编码
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        wav_buffer.seek(0)
        audio_base64 = base64.b64encode(wav_buffer.read()).decode('utf-8')

        return audio_base64

    except OSError as e:
        print(f"音频设备错误: {e}")
        print("\n尝试解决方案:")
        print("1. 检查麦克风是否连接并启用")
        print("2. 确保没有其他程序占用麦克风")
        print("3. 在Windows上，尝试以管理员权限运行")
        return None
    except Exception as e:
        print(f"录音过程中出错: {e}")
        return None


def send_audio_for_recognition(audio_data_base64):
    """发送音频数据进行语音识别"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    # 修改后的payload，直接包含音频数据
    payload = {
        "model": "asr",
        "audio": {
            "format": "wav",  # 修改为wav格式
            "data": audio_data_base64  # 直接发送base64编码的音频数据
        }
    }

    resp = requests.post(f"{BASE}/voice/asr", headers=headers, json=payload, timeout=60)
    print("HTTP状态码:", resp.status_code)

    resp.raise_for_status()
    data = resp.json()

    # 提取识别文本
    text = (data.get("data", {}).get("result", {}) or {}).get("text")
    return text or "<未识别到文本>"


def main():
    # 检查API密钥
    if not API_KEY:
        print("错误: 请设置API_KEY环境变量")
        return

    # 1. 录制音频
    audio_data = record_audio()

    # 2. 发送识别请求
    print("发送音频数据进行识别...")
    recognized_text = send_audio_for_recognition(audio_data)

    if recognized_text:
        print(f"\n识别结果: {recognized_text}")

        # 可选：保存识别结果到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"recognition_result_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(recognized_text)
        print(f"结果已保存到: recognition_result_{timestamp}.txt")


# # 替代方案：如果API不支持base64数据，可以先保存为临时文件再上传
# def record_and_upload_alternative():
#     """替代方案：保存为临时文件后上传URL"""
#     import tempfile
#     import urllib.parse

#     # 录制音频（返回WAV文件路径）
#     p = pyaudio.PyAudio()
#     stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

#     frames = []
#     print("开始录音...（5秒）")

#     for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     # 保存为临时文件
#     with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
#         with wave.open(temp_file.name, 'wb') as wf:
#             wf.setnchannels(CHANNELS)
#             wf.setsampwidth(p.get_sample_size(FORMAT))
#             wf.setframerate(RATE)
#             wf.writeframes(b''.join(frames))

#         temp_path = temp_file.name

#     print(f"音频已保存到: {temp_path}")

#     # 这里需要将文件上传到可公开访问的URL
#     # 由于这需要额外的文件存储服务，这里只是示意
#     print("注意：需要将文件上传到公网可访问的URL")
#     return temp_path


if __name__ == "__main__":
    # 从环境变量获取API配置
    API_KEY = LLMmain.openai_api_key
    BASE = os.getenv("QINIU_BASE_URL", "https://openai.qiniu.com/v1")

    # 检查pyaudio是否可用
    try:
        import pyaudio

        main()
    except ImportError:
        print("错误: 需要安装pyaudio库")
        print("安装命令: pip install pyaudio")
        # 在Windows上可能需要: pip install pipwin && pipwin install pyaudio