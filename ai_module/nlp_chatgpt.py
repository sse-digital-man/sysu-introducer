# from revChatGPT.V1 import Chatbot
# from utils import config_util as cfg
# import time 

# count = 0
# def question(cont):
#     global count
#     try:
#         chatbot = Chatbot(config={
#             "access_token": cfg.key_gpt_access_token,
#             "paid": False,
#             "collect_analytics": True,
#             "proxy": cfg.proxy_config,
#             "model": "gpt-4",
#             "conversation_id":cfg.key_gpt_conversation_id
#             },conversation_id=cfg.key_gpt_conversation_id,
#             parent_id=None)

#         prompt = cont
#         response = ""
#         for data in chatbot.ask(prompt):
#             response = data["message"]
#         count = 0
#         return response
#     except Exception as e:
#         count += 1
#         if count < 3:
#             time.sleep(15)
#             return question(cont)
#         return 'gpt当前繁忙，请稍后重试' + e

# 添加工作路径
import sys
sys.path.append("./ai_module")
sys.path.append("./ai_module/enhance")

from ai_module.enhance.bots.gpt_bot import GPTBot as Bot

def question(content):
    return Bot().talk(content)


if __name__ == '__main__':
    print(question("你是谁"))
    # from enhance.dboperator import DBOPT
    # DBOPT.query("你好")
