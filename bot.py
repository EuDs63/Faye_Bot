# telegramBot
# 功能：
# 基本的logger，后续打算完善下
# 指令：
# dog : 发送一张狗的图片
# save : save the word
# send : send the saved messages
# poetry : 发送一句诗
# en_poetry : 发送一首随机的英文诗

import random
import traceback
import datetime
import datetime
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from BingImageCreator import ImageGen
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode
from BingImageCreator import ImageGen
import requests
import re
import json
import os
import sys
import html

# 路径
root_path = os.path.dirname(__file__)
warning_path = os.path.join(root_path, 'warning.log')

# 日志的配置
logger = logging.getLogger(__name__)
# 我以为basicConfig设置后，file_handler就不用再设置Formatter，但实践发现不能
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler(filename=warning_path, mode='a', encoding='utf-8')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.WARNING)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)


# error_handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    DEVELOPER_CHAT_ID = 5405793578

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


# 实现dog指令
## 从random.dog中获取url
def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


## 返回符合要求后缀的url
def get_image_url():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


## dog指令
async def dog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = get_image_url()
    chat_id = update.message.chat_id
    logger.info(f"{chat_id},send a command '/dog'")
    await context.bot.send_photo(chat_id=chat_id, photo=url)


# 实现诗句指令
## 目前还只有古诗，下一步计划是添加外国诗句，并增加判断：如果是外国诗，应返回原文和译文
## 从https://v1.jinrishici.com/获取一句随机古诗
DEFAULT_SENTENCE = {
    "content": "黄河西来决昆仑，咆哮万里触龙门。",
    "origin": "公无渡河",
    "author": "李白"
}
SENTENCE_API = "https://v1.jinrishici.com/all"


def get_one_sentence():
    try:
        r = requests.get(SENTENCE_API).json()
        logger.info('call SENTENCE_API')
        return r
    except:
        logger.error("get SENTENCE_API wrong")
        return DEFAULT_SENTENCE


## /poetry指令
async def poetry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = get_one_sentence()
    content = r['content']
    title = r['origin']
    author = r['author']
    reply = f"\"{content}\"\n作者： {author}\n题目： {title}"
    chat_id = update.message.chat_id
    logger.info(f"{chat_id},send a command '/poetry'")
    await context.bot.send_message(chat_id=chat_id, text=reply)


## 从https://poetrydb.org随机获取一首英文诗，行数在14行以内
DEFAULT_POEM = [
    {
        "title": "Ozymandias",
        "author": "Percy Bysshe Shelley",
        "lines": [
            "I met a traveller from an antique land",
            "Who said: Two vast and trunkless legs of stone",
            "Stand in the desert...Near them, on the sand,",
            "Half sunk, a shattered visage lies, whose frown,",
            "And wrinkled lip, and sneer of cold command,",
            "Tell that its sculptor well those passions read",
            "Which yet survive, stamped on these lifeless things,",
            "The hand that mocked them, and the heart that fed:",
            "And on the pedestal these words appear:",
            "'My name is Ozymandias, king of kings:",
            "Look on my works, ye Mighty, and despair!'",
            "Nothing beside remains. Round the decay",
            "Of that colossal wreck, boundless and bare",
            "The lone and level sands stretch far away."
        ],
        "linecount": "14"
    }
]


def get_poem():
    try:
        linecount = random.randint(4, 14)
        POEM_API = f"https://poetrydb.org/random,linecount/1;{linecount}"
        r = requests.get(POEM_API).json()
        logger.info("call POEM_API successfully!")
        return r
    except:
        logger.info("get POEM_API wrong")
        return DEFAULT_POEM


## /en_poetry指令
async def en_poetry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    r = get_poem()
    lines = r[0]['lines']
    title = r[0]['title']
    author = r[0]['author']
    f_line = '\n'.join(lines)
    reply = f"\"{f_line}\"\nauthor: {author}\ntitle： {title}"
    chat_id = update.message.chat_id
    logger.info(f"{chat_id},send a command '/en_poetry'")
    await context.bot.send_message(chat_id=chat_id, text=reply)


# save_text指令
async def save_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # 获取当前时间
        now = datetime.datetime.now()
        now_time = now.strftime("%Y-%m-%d %H:%M:%S")

        # 获取用户id
        chat_id = update.effective_chat.id

        # 获取所要保存的文字
        text = update.message.text
        save_message = text[6:]

        # 获取消息id
        message_id = update.message.message_id

        # 写日志
        logger.info("{} save {}, at {}".format(chat_id, save_message, now_time))

        # 读取文件中的现有数据
        save_path = os.path.join(root_path, 'save.json')
        if os.path.exists(save_path):
            file_size = os.stat(save_path).st_size
            # 判断文件大小，若文件为空，则应令data = [].
            if file_size == 0:
                data = []
            else:
                with open(save_path, "r", encoding='utf-8') as read_file:
                    data = json.load(read_file)
        else:
            data = []

        # 添加
        new_data = {
            "time": now_time,
            "user": chat_id,
            "text": save_message
        }
        data.append(new_data)

        # 保存到save.json文件中
        save_path = os.path.join(root_path, 'save.json')
        with open(save_path, "w", encoding='UTF-8') as write_file:
            write_file.write(json.dumps(data, ensure_ascii=False, indent=2))
            write_file.write('\n')

        # 设置回复消息
        reply = "save successfully , saved message is " + save_message

    except Exception as e:
        # print("Something went wrong!")
        logger.error("encounter error {} when save {}".format(e, text))

    # 回复
    await context.bot.send_message(chat_id=chat_id, text=reply, reply_to_message_id=message_id)


# send 用户有两种选择，一种是让bot直接输出所存储的信息，另一种是让bot发送save.json文件

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

# inline的方式,给用户提供选择
async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choose_keyboard = [
        [InlineKeyboardButton("message", callback_data="send_message")],
        [InlineKeyboardButton("file", callback_data="send_file")],
    ]

    reply_markup = InlineKeyboardMarkup(choose_keyboard)

    await update.message.reply_text("Which way do you want to get the saved message ?", reply_markup=reply_markup)
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
async def send_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == 'send_message':
        await query.answer()
        await query.edit_message_text(text="Sending message...")
        await send_message(update, context)

    elif data == 'send_file':
        await query.answer()
        await query.edit_message_text(text="Sending file...")
        await send_file(update, context)


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # 获取用户id
        chat_id = update.effective_chat.id

        logger.info("try to send saved message to {}".format(chat_id))

        save_path = os.path.join(root_path, 'save.json')
        if os.path.exists(save_path):
            logger.info("send saved message to {}".format(chat_id))
            with open(save_path, "r", encoding='utf-8') as read_file:
                messages = []
                data = json.load(read_file)
                num_messages = len(data)
                display_count = 10  # 每十条输出一次
                pages = num_messages // display_count
                real_pages = pages if ((num_messages % display_count) == 0) else (pages + 1)
                # 根据所选的页数展示相关的记录
                choose_page = 1
                off = 1 + display_count * (choose_page - 1)
                for i in range(off, off + display_count if (choose_page < real_pages) else num_messages):
                    messages.append(f"{i}. {data[i]['text']}")
                text = '\n'.join(messages)

                keyboard = [
                    [InlineKeyboardButton(f"{i}", callback_data="page" + str(i)) for i in range(1, real_pages + 1)]]
                reply_markup = InlineKeyboardMarkup(keyboard)

            # await context.bot.sendMessage(chat_id=chat_id,text=text)
            await context.bot.sendMessage(chat_id=chat_id, text=text, reply_markup=reply_markup)
        else:
            await context.bot.sendMessage(chat_id=chat_id, text="sorry,you havn't save anything")

    except Exception as e:
        print("Something went wrong!")
        logger.error("encounter error {} when send saved message".format(e))


# 实现分页功能
async def send_message_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    choose_page = int(query.data[4])

    if (choose_page > 0):
        save_path = os.path.join(root_path, 'save.json')
        with open(save_path, "r", encoding='utf-8') as read_file:
            messages = []
            data = json.load(read_file)
            num_messages = len(data)
            display_count = 10  # 每十条输出一次
            pages = num_messages // display_count
            real_pages = pages if ((num_messages % display_count) == 0) else (pages + 1)
            # 根据所选的页数展示相关的记录
            off = 1 + display_count * (choose_page - 1)
            for i in range(off, off + display_count if (choose_page < real_pages) else num_messages):
                messages.append(f"{i}. {data[i]['text']}")
                text = '\n'.join(messages)

            keyboard = [
                [
                    InlineKeyboardButton(f"{i}", callback_data="page" + str(i)) for i in range(1, real_pages + 1)
                ],
                [InlineKeyboardButton("over", callback_data="page" + str(0))],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=text, reply_markup=reply_markup)
    else:
        await query.edit_message_text(text="send_message over. Bye!")

    await query.answer()


# send_save 发送储存的save_json文件
async def send_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # 获取用户id
        chat_id = update.effective_chat.id
        logger.info("try to send save.json to {}".format(chat_id))
        save_path = os.path.join(root_path, 'save.json')
        if os.path.exists(save_path):
            logger.info("send save.json to {}".format(chat_id))
            await context.bot.sendDocument(chat_id=chat_id, document=open(save_path, 'rb'))

        else:
            await context.bot.sendMessage(chat_id=chat_id, text="sorry,you havn't save anything")

    except Exception as e:
        print("Something went wrong!")
        logger.error("encounter error {} when send file".format(e))

    #


async def reply_dalle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    bot = context.bot
    chat_id = update.message.chat_id
    start_words = "/bing "
    if not message.text.startswith(start_words):
        return
    print(message.from_user.id)
    path = os.path.join("images", str(message.from_user.id))
    if not os.path.exists(path):
        os.mkdir(path)
    s = message.text[len(start_words):].strip()
    i = ImageGen(bing_cookie)
    # await bot.sendMessage(chat_id=message.from_user.id, text="Using bing DALL-E 3 generating images please wait")
    images = i.get_images(s)
    i.save_images(images, path)
    images_count = len(list(os.listdir(path)))
    # print(images_count)
    index = random.randint(images_count - len(images), images_count - 1)
    with open(os.path.join(path, str(index)) + ".jpeg", "rb") as f:
        await bot.send_photo(message.chat.id, f, reply_to_message_id=message.message_id)
    return


# main方法
if __name__ == '__main__':
    config_path = os.path.join(root_path, 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    proxy_url = config['proxy_url']
    token = config['token']
    bing_cookie = config['bing_cookie']

    application = ApplicationBuilder().token(token).proxy_url(proxy_url).get_updates_proxy_url(proxy_url).build()  # 非容器
    # application = ApplicationBuilder().token(token).build() #容器

    dog_handler = CommandHandler('dog', dog)
    save_handler = CommandHandler('save', save_text)
    send_handler = CommandHandler('send', send)
    sendChoose_handler = CallbackQueryHandler(send_choose)
    send_message_choose_handler = CallbackQueryHandler(send_message_choose, pattern="^page")

    poetry_handler = CommandHandler('poetry', poetry)
    en_poetry_handler = CommandHandler('en_poetry', en_poetry)

    bing_handler = CommandHandler('bing', reply_dalle_image)

    application.add_handler(dog_handler)
    application.add_handler(save_handler)
    application.add_handler(send_handler)
    application.add_handler(send_message_choose_handler)
    application.add_handler(sendChoose_handler)
    application.add_handler(poetry_handler)
    application.add_handler(en_poetry_handler)
    application.add_error_handler(error_handler)
    application.add_handler(bing_handler)

    if not os.path.exists("images"):
        os.mkdir("images")

    application.run_polling()
