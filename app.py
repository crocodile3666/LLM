from flask import Flask, render_template, request, jsonify
import time
import random
import LLMmain
app = Flask(__name__)
import webbrowser
import threading

def get_ai_fristsentence():
    responses = LLMmain.fristsentence
    return responses


@app.route('/')
def index():
    welcome_message = get_ai_fristsentence()
    return render_template('index.html',welcome_message = welcome_message )

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        return jsonify({'error': '消息不能为空'}), 400

    # 获取AI响应
    ai_response = LLMmain.chat_with_memory(user_message)

    return jsonify({
        'user_message': user_message,
        'ai_response': ai_response,
        'timestamp': time.strftime('%H:%M:%S')
    })

def open_browser():
    # 等待服务器完全启动
    time.sleep(1.5)
    # 打开默认浏览器访问服务器
    webbrowser.open('http://127.0.0.1:5001')

if __name__ == '__main__':

    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # 生产环境：使用Waitress服务器
    from waitress import serve

    print("正在启动Waitress生产服务器...")
    serve(app, host='127.0.0.1', port=5001)
