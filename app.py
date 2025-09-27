from flask import Flask, render_template, request, jsonify
import time
import random
import LLMmain
app = Flask(__name__)


# 大模型响应函数
def get_ai_response(user_message):
    # 模拟处理时间
    time.sleep(1)

    # 简单的响应逻辑 - 实际使用时可以替换为真实的大模型API调用
    responses = [
        f"我理解您说的是：'{user_message}'。这是一个很有趣的观点。",
        f"关于'{user_message}'，我认为这涉及到多个方面的考虑。",
        "您提出的问题很有深度，让我思考一下如何回答。",
        "根据我的理解，您的问题可以这样看待...",
        "这是一个很好的问题！让我为您详细解释一下。"
    ]

    return random.choice(responses)

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

if __name__ == '__main__':
    # 开发环境：使用Flask内置服务器（带调试功能）
    # app.run(debug=True)

    # 生产环境：使用Waitress服务器
    from waitress import serve

    print("正在启动Waitress生产服务器...")
    serve(app, host='127.0.0.1', port=5001)