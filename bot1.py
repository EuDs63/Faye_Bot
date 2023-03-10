# telegramBot
# 功能：
# 基本的logger，后续打算完善下 
# 指令：
# dog : 发送一张狗的图片
import logging
from telegram import Update
from  telegram.ext import ApplicationBuilder,ContextTypes,CommandHandler,MessageHandler,filters
import requests
import re
import json
import os
import openai
import textwrap


messages =[]
messages.append({"role":"system","content":"你是一个大学学生，回答问题应简洁"})
# 日志的配置
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 从random.dog中获取url
def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url

# 返回符合要求后缀的url
def get_image_url():
    allowed_extension = ['jpg','jpeg','png']
    file_extension =''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

# start指令
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    #logging.Logger("hello,world")
    chat_id=update.effective_chat.id
    info ="{} send a command '/start'".format(chat_id)
    logger.info(info)
    await context.bot.send_message(chat_id=chat_id,text="Nice to meet you!")

# dog指令
async def dog(update:Update,context: ContextTypes.DEFAULT_TYPE):
    url = get_image_url()
    chat_id = update.message.chat_id
    await context.bot.send_photo(chat_id = chat_id,photo=url)

# openAI
async def echo(update:Update,context:ContextTypes.DEFAULT_TYPE):
    lines_printed = 0
    result = ""
    try:
        text =update.message.text
        chat_id = update.effective_chat.id
        logger.info("{} : {}".format(chat_id,text))
        messages.append({"role":"user","content":text})
        formatted_parts = []
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=messages
        )
        reply = response["choices"][0]["message"]["content"]
        logger.info("reply: {}".format(reply))
        # for message in reply:
        #     # Split the message by newlines
        #     message_parts = message['message'].split('\n')

        #     # Wrap each part separately
        #     formatted_parts = []
        #     for part in message_parts:
        #         formatted_parts.extend(textwrap.wrap(part, width=80))
        #         for formatted_line in formatted_parts:
        #             if (len(formatted_parts) > lines_printed ):
        #                 result += formatted_parts[lines_printed]
        #                 print(formatted_parts[lines_printed])
        #                 lines_printed += 1
        # result += formatted_parts[lines_printed]
        # print(formatted_parts[lines_printed])
    except Exception as e:
        print("Something went wrong!")
        print(e)
        print("sorry to tell you about that!")

    await context.bot.send_message(chat_id=chat_id, text=reply)




# main方法
if __name__ == '__main__':
    config_path = os.path.join(os.path.dirname(__file__),'config.json')
    with open(config_path,'r') as f:
        config = json.load(f)
    #print(config)
    proxy_url = config['proxy_url'] 
    token = config['token'] 
    openai.api_key=config['api_key']
    application = ApplicationBuilder().token(token).proxy_url(proxy_url).get_updates_proxy_url(proxy_url).build()

    start_handler = CommandHandler('start',start)
    dog_handler = CommandHandler('dog',dog)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND),echo)

    application.add_handler(start_handler)
    application.add_handler(dog_handler)
    application.add_handler(echo_handler)

    application.run_polling()
