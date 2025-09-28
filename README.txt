模型对话在“对话网页.bat”中打开
由于前端不太会
TTS服务需要在TTS.py文件使用TTS(语音转文本)函数调用来获得
ASR需要在线音频文件并在ASR.py文件使用ASR(URL)函数来调用
角色提示词需要在LLMRoleCreation.py中进行定义并替换LLMmain.py中的system_template，再启动"对话网页.bat"