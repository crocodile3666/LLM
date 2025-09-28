from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from typing import List, Dict, Any, Optional
import LLMRoleCreation
openai_base_url = 'https://openai.qiniu.com/v1'
openai_api_key = 'yourapi'
client = OpenAI(
    base_url=openai_base_url,
    api_key=openai_api_key
)
model="deepseek-v3"
def convert_to_openai_format(messages):
    openai_messages = []
    for message in messages:
        openai_messages.append({
            "role": message.type,  # system, human, ai 需要映射
            "content": message.content
        })
    return openai_messages

from langchain_core.prompts import ChatPromptTemplate

system_template = LLMRoleCreation.Known_information()
prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template)]
)
prompt = prompt_template
prompt = prompt_template.invoke({"text":  "现在，请以扮演的角色的身份开始我们的对话，首先对我说第一句话。"})

# 转换为七牛云api符合的格式
messages = convert_to_openai_format(prompt.to_messages())
for msg in messages:
    if msg["role"] == "human":
        msg["role"] = "user"
    elif msg["role"] == "ai":
        msg["role"] = "assistant"
response = client.chat.completions.create(
    model="deepseek-v3",
    messages=messages,
    stream=True,  # 启用流式输出
    max_tokens=4096
)

# 处理流式响应
fristsentence = ""
for chunk in response:
    if chunk.choices[0].delta.content is not None:
        chunk_content = chunk.choices[0].delta.content
        fristsentence += chunk_content
        # print(chunk_content, end="", flush=True)
# print(f"\n\n完整回复: {fristsentence}")




class ContextMemory:
    def __init__(self, max_messages: int = 20, summary_threshold: int = 10):
        self.messages = []
        self.max_messages = max_messages
        self.summary_threshold = summary_threshold
        self.summary = []
    def add_message(self, role: str, content: str):
        """添加消息到记忆，并自动提取实体"""
        message = {"role": role, "content": content}
        self.messages.append(message)

        # 如果消息数量超过阈值，进行概括
        if len(self.messages) >= self.summary_threshold:
            self._summarize_conversation()

    def _summarize_conversation(self):
        if len(self.messages) < 5:  # 至少5条消息才进行概括
            return

        # 获取最近的消息进行概括（可以根据需要调整数量）
        recent_messages = self.messages[-10:]  # 取最近10条消息

        # 准备概括的提示词
        summary_messages = [
            {
                "role": "system",
                "content": "你是一个专业的对话总结助手。请用简洁明了的语言概括以下对话的主要内容、关键点和结论。保持总结客观准确，长度在100-200字之间。"
            },
            {
                "role": "user",
                "content": "请概括以下对话：\n" + "\n".join([
                    f"{msg['role']}: {msg['content']}" for msg in recent_messages
                ])
            }
        ]

        # 转换消息格式（如果需要）
        formatted_messages = []
        for msg in summary_messages:
            formatted_msg = msg.copy()
            if formatted_msg["role"] == "human":
                formatted_msg["role"] = "user"
            elif formatted_msg["role"] == "ai":
                formatted_msg["role"] = "assistant"
            formatted_messages.append(formatted_msg)

        # 调用AI接口进行概括
        response = client.chat.completions.create(
            model="deepseek-v3",
            messages=formatted_messages,
            stream=False,  # 概括不需要流式输出
            max_tokens=500,
            temperature=0.3  # 较低的温度以获得更稳定的总结
        )

        # 获取概括结果
        self.summary = response.choices[0].message.content.strip()
        # print(f"对话概括完成: {self.summary}")

    def get_context_prompt(self) -> str:
        """获取上下文提示信息"""
        context_prompt = ""

        if self.summary:
            context_prompt += f"对话概括: {self.summary}\n\n"

        # 添加最近几条消息作为上下文
        recent_count = min(3, len(self.messages))
        if recent_count > 0:
            context_prompt += "最近对话:\n"
            for msg in self.messages[-recent_count:]:
                context_prompt += f"{msg['role']}: {msg['content'][:200]}...\n"

        return context_prompt

    def get_enhanced_messages(self, new_message: str) -> List[Dict[str, str]]:
        """获取增强后的消息列表"""
        enhanced_messages = []
        system_prompttmp = f"""以下是当前对话的上下文信息：

        {self.get_context_prompt()}

        请基于以上上下文信息进行回复。"""
        system_template_chat = system_template + system_prompttmp
        enhanced_messages.append({"role": "system", "content": system_template_chat})
        # 添加新消息
        enhanced_messages.append({"role": "user", "content": new_message})

        return enhanced_messages
def chat_with_memory(user_input: str):
    # 添加到记忆
    memory.add_message("user", user_input)

    # 获取增强后的消息
    enhanced_messages = memory.get_enhanced_messages(user_input)

    client = OpenAI(
        base_url=openai_base_url,
        api_key=openai_api_key
    )

    response = client.chat.completions.create(
        model="deepseek-v3",
        messages=enhanced_messages,
        stream=True,
        max_tokens=4096
    )

    # 收集AI回复
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            # print(content, end="", flush=True)

    # 将AI回复添加到记忆
    memory.add_message("assistant", full_response)

    return full_response

memory = ContextMemory()
# user_input = "抱歉"
# chat_with_memory(user_input)
# user_input = "那你能告诉我魔药学的最新进展吗？"
# chat_with_memory(user_input)
#
# user_input = "能展开讲讲吗？"
# chat_with_memory(user_input)
#
# user_input = "我很感兴趣其中的前沿方向可以具体讲讲吗？"
# chat_with_memory(user_input)
#
# user_input = "能给个完整的项目落地方案吗？"
# chat_with_memory(user_input)
# print("对话概括:", memory.summary)