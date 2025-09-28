import LLMmain
import TTS

def simple_chat():
    frist = LLMmain.fristsentence
    print(f"AI:{frist}")
    TTS.TTS(frist)
    while True:
        user_input = input("你: ")

        if user_input.lower() in ['退出', 'exit', 'quit']:
            print("AI: 再见！")
            break

        response = LLMmain.chat_with_memory(user_input)

        print(f"AI: {response}")
        TTS.TTS(response)

simple_chat()