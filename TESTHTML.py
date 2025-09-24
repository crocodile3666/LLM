import streamlit as st
import time
import random

# 设置页面标题和布局
st.set_page_config(
    page_title="AI对话助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_role" not in st.session_state:
    st.session_state.current_role = "通用助手"

if "audio_enabled" not in st.session_state:
    st.session_state.audio_enabled = False


# 模拟大模型响应
def get_ai_response(user_input, role):
    # 这里应该是调用真实的大模型API
    # 为了演示，我们使用简单的模拟响应
    time.sleep(1)  # 模拟网络延迟

    role_responses = {
        "通用助手": "这是一个通用的回答，我可以帮助您解决各种问题。",
        "编程专家": "关于编程问题，我建议您先检查代码语法，然后逐步调试。",
        "语言教师": "学习语言需要持之以恒的练习，我建议每天至少学习30分钟。",
        "心理咨询师": "我理解您的感受，让我们一起来探讨这个问题。",
        "创意作家": "这是一个很有创意的想法！我们可以进一步扩展这个构思。"
    }

    base_response = role_responses.get(role, "我理解您的意思。")

    # 根据输入生成更相关的响应
    if "你好" in user_input or "hello" in user_input.lower():
        return f"{base_response} 您好！很高兴与您交流。"
    elif "?" in user_input or "？" in user_input:
        return f"{base_response} 您的问题很有趣，让我思考一下。"
    else:
        return f"{base_response} 您提到的内容很有价值。"


# 侧边栏 - 角色选择
with st.sidebar:
    st.title("🤖 角色选择")

    roles = {
        "通用助手": "🦸",
        "编程专家": "💻",
        "语言教师": "📚",
        "心理咨询师": "🧠",
        "创意作家": "✍️"
    }

    selected_role = st.radio(
        "选择对话角色:",
        list(roles.keys()),
        index=list(roles.keys()).index(st.session_state.current_role)
    )

    if selected_role != st.session_state.current_role:
        st.session_state.current_role = selected_role
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # 音频设置
    st.subheader("音频设置")
    audio_enabled = st.toggle("启用语音", value=st.session_state.audio_enabled)
    if audio_enabled != st.session_state.audio_enabled:
        st.session_state.audio_enabled = audio_enabled
        st.rerun()

    st.divider()

    # 对话历史管理
    st.subheader("对话管理")
    if st.button("清空对话历史"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    # 说明
    st.info("""
    **使用说明:**
    1. 选择左侧的角色
    2. 在下方输入问题
    3. 点击发送或按Enter键
    4. 启用语音可听到回复
    """)

# 主界面
st.title(f"{roles[st.session_state.current_role]} {st.session_state.current_role}")

# 显示对话历史
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and st.session_state.audio_enabled:
                st.button("🔊", key=message.get("key", "default"), disabled=True)

# 用户输入区域
with st.container():
    col1, col2 = st.columns([6, 1])

    with col1:
        user_input = st.chat_input(f"向{st.session_state.current_role}提问...")

    with col2:
        if st.session_state.audio_enabled:
            audio_status = "🔊 开"
        else:
            audio_status = "🔇 关"

        if st.button(audio_status, use_container_width=True):
            st.session_state.audio_enabled = not st.session_state.audio_enabled
            st.rerun()

# 处理用户输入
if user_input:
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": user_input})

    # 显示用户消息
    with chat_container:
        with st.chat_message("user"):
            st.write(user_input)

    # 获取AI响应
    with st.spinner(f"{st.session_state.current_role}正在思考..."):
        ai_response = get_ai_response(user_input, st.session_state.current_role)

    # 添加AI响应到历史
    response_key = f"response_{len(st.session_state.messages)}"
    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response,
        "key": response_key
    })

    # 显示AI响应
    with chat_container:
        with st.chat_message("assistant"):
            st.write(ai_response)
            if st.session_state.audio_enabled:
                st.button("🔊", key=response_key, disabled=True)

# 添加自定义CSS样式
st.markdown("""
<style>
    .stButton button {
        width: 100%;
    }

    .stChatMessage {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)