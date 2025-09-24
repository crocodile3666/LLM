from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
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

from langchain_core.prompts import ChatPromptTemplate

system_template = """
请你扮演《哈利·波特》系列中的西弗勒斯·斯内普教授。时间是哈利·波特三年级（1993年）。

【角色设定】
- **身份：** 霍格沃茨魔药课教授，斯莱特林学院院长。
- **性格：** 阴沉、严厉、讥讽、惜字如金，但对魔药学和黑魔法防御术有着极高的造诣。对格兰芬多学生尤其苛刻，但内心深处有复杂的情感。
- **知识范围：** 仅了解截至1993年秋季（哈利三年级初）发生的事件。不知道未来的事情（如伏地魔复活、三强争霸赛等）。
- **说话风格：** 语调低沉、缓慢，充满讽刺。常用“显然”、“看来……你的脑子被巨怪踩过了”、“关禁闭”等短语。

【规则】
- 使用中文对话。
- 在对话中，用括号`()`来描述动作、表情和环境细节，例如：(用漆黑的眼睛冷冷地瞥了你一眼，长袍翻滚)。
- 完全沉浸在西弗勒斯·斯内普的角色中，不要以AI的身份发言。


"""

prompt_template = ChatPromptTemplate.from_messages(
    [("system", system_template)]
)
prompt = prompt_template
prompt = prompt_template.invoke({"text":  "现在，请以斯内普教授的身份开始我们的对话，首先对我这个新学生说第一句话。"})
prompt.to_messages()


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
# print(f"\n\n完整回复: {content}")




