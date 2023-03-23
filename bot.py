# telegramBot
# 功能：
# 基本的logger，后续打算完善下 
# 指令：
# dog : 发送一张狗的图片
# save : save the word
# send : send the saved messages

import traceback
import datetime
import datetime
import logging
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from  telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode
import requests
import re
import json
import os
import openai
import sys
import html


messages =[]
messages.append({"role":"system","content":"你是一个富有经验的大学老师，回答问题应简洁且准确"})

# 路径
root_path = os.path.dirname(__file__)

# 日志的配置
logger = logging.getLogger(__name__)
#我以为basicConfig设置后，file_handler就不用再设置Formatter，但实践发现不能
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

warning_path = os.path.join(root_path,'warning.log')
file_handler = logging.FileHandler(filename=warning_path,mode='a',encoding='utf-8')
file_handler.setFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setLevel(logging.WARNING)


logger.addHandler(logging.StreamHandler(sys.stdout))
logger.addHandler(file_handler)

#error_handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    DEVELOPER_CHAT_ID=5405793578

    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
    )


# start指令
async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    chat_id=update.effective_chat.id
    info ="{} send a command '/start'".format(chat_id)
    logger.info(info)
    await context.bot.send_message(chat_id=chat_id,text="Nice to meet you!")

#实现dog指令
## 从random.dog中获取url
def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url

## 返回符合要求后缀的url
def get_image_url():
    allowed_extension = ['jpg','jpeg','png']
    file_extension =''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

## dog指令
async def dog(update:Update,context: ContextTypes.DEFAULT_TYPE):
    url = get_image_url()
    chat_id = update.message.chat_id
    logger.info(f"{chat_id},send a command '/dog'")
    await context.bot.send_photo(chat_id = chat_id,photo=url)

# 接入gpt
async def echo(update:Update,context:ContextTypes.DEFAULT_TYPE):
    try:
        text =update.message.text
        chat_id = update.effective_chat.id
        logger.info("{} : {}".format(chat_id,text))
        messages.append({"role":"user","content":text})

        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=messages
        )
        reply = response["choices"][0]["message"]["content"]
        logger.info("reply: {}".format(reply))

    except Exception as e:
        print("Something went wrong!")
        print(e)
        print("sorry to tell you about that!")

    await context.bot.send_message(chat_id=chat_id, text=reply)

#save_text指令
async def save_text(update:Update,context:ContextTypes.DEFAULT_TYPE):
    try:
         #获取当前时间
         now = datetime.datetime.now()
         now_time = now.strftime("%Y-%m-%d %H:%M:%S")    

         #获取用户id
         chat_id = update.effective_chat.id

         #获取所要保存的文字
         text =update.message.text
         save_message = text[6:]

         #获取消息id
         message_id = update.message.message_id

        #写日志
         logger.info("{} save {}, at {}".format(chat_id,save_message,now_time))

        # 读取文件中的现有数据
         save_path = os.path.join(root_path, 'save.json')
         if os.path.exists(save_path):
            file_size = os.stat(save_path).st_size
            # 判断文件大小，若文件为空，则应令data = []. 
            if file_size == 0:
                data = []
            else:
                with open(save_path, "r",encoding='utf-8') as read_file:
                    data = json.load(read_file)
         else:
            data = []

        # 添加
         new_data = {
            "time" : now_time,
            "user" : chat_id,
            "text" : save_message
         }
         data.append(new_data)
        
        # 保存到save.json文件中
         save_path = os.path.join(root_path,'save.json')
         with open(save_path,"w",encoding='UTF-8') as write_file:
            write_file.write(json.dumps(data,ensure_ascii=False,indent=2))
            write_file.write('\n')
    
        # 设置回复消息
         reply = "save successfully , saved message is "+save_message

    except Exception as e:
        print("Something went wrong!")
        logger.error("encounter error {} when save {}".format(e,text))

    # 回复
    await context.bot.send_message(chat_id=chat_id, text=reply,reply_to_message_id=message_id)


#send 用户有两种选择，一种是让bot直接输出所存储的信息，另一种是让bot发送save.json文件

# 这个是让用户输入信息，但是会影响到openai接口的功能，所以放弃了
# 解决方法：设置正则，去挑选以message和file开头的，但是比较丑陋

# async def send(update:Update,context:ContextTypes.DEFAULT_TYPE):
#     reply_keyboard =[["message","file"]]

#     await update.message.reply_text(
#         "Which way do you want to get the saved message ?\n",
#         reply_markup=ReplyKeyboardMarkup(
#             reply_keyboard, one_time_keyboard=True,input_field_placeholder="message or file?"
#         ),
#     )

#     return send_choose

#inline的方式,给用户提供选择
async def send(update:Update,context:ContextTypes.DEFAULT_TYPE):
    choose_keyboard = [
        [InlineKeyboardButton("message", callback_data="1")],
        [InlineKeyboardButton("file", callback_data="2")],
    ]

    reply_markup = InlineKeyboardMarkup(choose_keyboard)

    await update.message.reply_text("Which way do you want to get the saved message ?",reply_markup=reply_markup)
    # choose = update.message.text
    # logging.info("{} choose {} to get the saved content".format(update.effective_chat.id,choose))
    # if choose=="file" :
    #     return send_save
    # else :
    #     return send_message

# async def send_choose(update:Update,context:ContextTypes.DEFAULT_TYPE):
#     choose = update.message.text
#     logging.info("{} choose {} to get the saved content".format(update.effective_chat.id,choose))
#     if choose=="file" :
#         return send_save
#     else :
#         return send_message

# 判断用户的选择
async def send_choose(update:Update,context:ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data =='1':
        await query.answer()
        await query.edit_message_text(text="Sending message...")
        await send_message(update,context)

    elif data =='2':
        await query.answer()
        await query.edit_message_text(text="Sending file...")
        await send_file(update,context)

async def send_message(update:Update,context:ContextTypes.DEFAULT_TYPE):
    try:
         #获取用户id
         chat_id = update.effective_chat.id

         logger.info("try to send saved message to {}".format(chat_id))

         save_path = os.path.join(root_path, 'save.json')
         if os.path.exists(save_path):
            logger.info("send saved message to {}".format(chat_id))
            with open(save_path, "r",encoding='utf-8') as read_file:
                messages = []
                data = json.load(read_file)
                for index,obj in enumerate(data):
                    messages.append(f"{index+1}. {obj['text']}")
                text = '\n'.join(messages)
            # await context.bot.sendMessage(chat_id=chat_id,text=json.dumps(text, ensure_ascii=False)) #这里之前忘记修改了，导致输出有问题
            await context.bot.sendMessage(chat_id=chat_id,text=text)

         else:
            await context.bot.sendMessage(chat_id=chat_id,text="sorry,you havn't save anything")
            
    except Exception as e:
        print("Something went wrong!")
        logger.error("encounter error {} when send saved message".format(e))

#send_save 发送储存的save_json文件
async def send_file(update:Update,context:ContextTypes.DEFAULT_TYPE):
    try:
         #获取用户id
         chat_id = update.effective_chat.id
         logger.info("try to send save.json to {}".format(chat_id))
         save_path = os.path.join(root_path, 'save.json')
         if os.path.exists(save_path):
            logger.info("send save.json to {}".format(chat_id))
            await context.bot.sendDocument(chat_id=chat_id,document=open(save_path,'rb'))

         else:
            await context.bot.sendMessage(chat_id=chat_id,text="sorry,you havn't save anything")
            
    except Exception as e:
        print("Something went wrong!")
        logger.error("encounter error {} when send file".format(e))
    
# async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Cancels and ends the conversation."""
#     user = update.message.from_user
#     logger.info("User %s canceled the conversation.", user.first_name)
#     await update.message.reply_text(
#         "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
#     )

#     return ConversationHandler.END

# main方法
if __name__ == '__main__':
    config_path = os.path.join(root_path,'config.json')
    with open(config_path,'r') as f:
        config = json.load(f)
    #print(config)
    proxy_url = config['proxy_url'] 
    token = config['token'] 
    openai.api_key=config['api_key']
    #application = ApplicationBuilder().token(token).proxy_url(proxy_url).get_updates_proxy_url(proxy_url).build() #非容器
    application = ApplicationBuilder().token(token).build() #容器

    start_handler = CommandHandler('start',start)
    dog_handler = CommandHandler('dog',dog)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND),echo)
    save_handler = CommandHandler('save',save_text)
    send_handler = CommandHandler('send',send)
    sendChoose_handler = CallbackQueryHandler(send_choose)

    # send_handler = ConversationHandler(
    #     entry_points= [CommandHandler("send",send)],
    #     states={
            
    #     }
    #     fallbacks=[CommandHandler("cancel", cancel)],
    # )



    application.add_handler(start_handler)
    application.add_handler(dog_handler)
    application.add_handler(echo_handler)
    application.add_handler(save_handler)
    application.add_handler(send_handler)
    application.add_handler(sendChoose_handler)
    application.add_error_handler(error_handler)


    application.run_polling()
