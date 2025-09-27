from openai import OpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate

openai_base_url = 'https://openai.qiniu.com/v1'
openai_api_key = 'sk-c80c48d9f23cdd2afd5835fed42329fdd10a0b69e5e5dee3e5875b63a28e8290'
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
#
#
enhanced_messages = []
system_template = """
请你扮演{name}。时间是{time}。
用户叫{user},是{userstory}

【角色设定】
- 身份：{role}
- 性格：{personality}
- 知识范围：{knowledge}
- 说话风格：{style}

【规则】
- 使用中文对话。
- 在对话中，用括号`()`来描述动作、表情和环境细节。
- 完全沉浸在角色中，不要以AI的身份发言。
"""

enhanced_messages.append({"role": "system", "content": system_template})

name=[]
time=[]
user=[]
userstory=[]
role=[]
personality=[]
knowledge=[]
style=[]

# 填入具体参数
filled_system_template = system_template.format(
    name="Sherlock Holmes",
    time="维多利亚时代的伦敦",
    user="John Watson",
    userstory="你的得力助手",
    role="著名侦探",
    personality="观察力敏锐、逻辑严谨、略带傲慢",
    knowledge="犯罪学、化学、解剖学、伦敦街头知识",
    style="冷静分析，喜欢使用演绎法，语气自信",
)
prompt_template = ChatPromptTemplate.from_messages(
    [("system", filled_system_template)]
)
prompt = prompt_template.invoke({"text":  "现在，请以扮演的角色的身份开始我们的对话，首先对我说第一句话。"})
print(prompt)


messages = convert_to_openai_format(prompt.messages)
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

fristsentence = ""
for chunk in response:
    if chunk.choices[0].delta.content is not None:
        chunk_content = chunk.choices[0].delta.content
        fristsentence += chunk_content
        print(chunk_content, end="", flush=True)
print(f"\n\n完整回复: {fristsentence}")

