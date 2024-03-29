# README

## 介绍
基于python的telegram bot，现支持功能
- /dog 返回一张随机的狗的照片
- 通过api接入了ChatGPT，支持直接对话
- /save : save the word
- /send : send the saved messages
- /poetry : 发送一句诗
- /en_poetry : 发送一首随机的英文诗
- /bing : 根据其后所跟的prompt，使用dalle-3生成对应的图片

## command
```
dog - send a dog picture
save - save the word
send - send the saved messages
poetry - send a poem
en_poetry - send a random English poem
bing - send a picture drawn by dalle-3
```


## ToDo
- [x] 学习完善Dockerfile，docker-compose的配置
- [ ] 完善日志设置，保存聊天记录 
- ~~修改代码，现在似乎是会不断把之前的记录叠加？~~
- [ ] build的image过大（1g出头），将其瘦身
- [x] 添加指令`\save` 保存其后的文字
- [ ] 当save.json每次有改变时，更新到博客上
- [ ] 模块化
- [x] file_log 有问题，无法正确log
- [ ] 在config.json中设置是否使用gpt
- ~~[ ] 扩展poestry指令的功能，添加外国诗句，并增加判断：如果是外国诗，应返回原文和译文~~
- [x] 添加指令 可以返回一首随机的英文诗
- [ ] 使用[bing画图](https://www.bing.com/create)，给诗句配图
- [ ] 定时发送诗句
- [ ] 增强稳定性。bot会因为网络不够稳定导致需要重启。我目前的解决方法是使用crontab来定时重启，但觉得应该有更好的方法。

## 部署
提供了两种方法

- 自行编译
```
# 自行编译
docker build -t fayebot .
# Windows系统
# docker run --e httpproxy="http://host.docker.internal:7890" fayebot 
# Linux 系统
docker run --e httpproxy="http://172.17.0.1:7890" fayebot
```

- 使用docker-compose(推荐)
```
mkdir Faye_Bot
cd Faye_Bot
wget https://raw.githubusercontent.com/EuDs63/Faye_Bot/master/docker-compose.yml
wget https://raw.githubusercontent.com/EuDs63/Faye_Bot/master/bot.py
vim save.json
vim warning.log
vim config.json # 内容参见config.json.example
docker-compose up -d
```

## 历程
去年12月的时候就想过要搭一个telegramBot,也搭出来了，但功能不是很完善，所以想趁着最近比较闲加上有一个服务器来好好做。之前的文件有点乱，就重开了一个文件夹。

- 3月11日，想部署到服务器上。
  - 先是因为pip版本太低，导致安装依赖时报错 `no matching distribution found for`；
  - 升级python版本
  - 运行时报错`ModuleNotFoundError: No module named '_ssl'`,尝试多种方法，未果。
  暂时放弃，认识到配环境的困难，决定改用docker
- 3月12日，学习使用docker。遇到的最大的问题是网络问题。具体来说是容器内部访问网络问题：
  - 通过配置docker-compose文件来实现，但未能成效，可能是因为一些参数的问题
  - 修改Dockerfile文件，同上
  - 在Docker Desktop -> seetings -> Docker Engine修改文件后，软件一直处于卡死状态，无奈还原修改的文件
  - 尝试在run image时添加命令，如`docker run --env httpproxy="http://172.17.0.1:7890" fayebot`，成功了，但发现若配置了httpsproxy则不行，未知其因.("可能是没有给Docker配置TLS证书？")
- 3月22日，添加指令/save,/send,遇到的问题有
  - json文件的编码格式
  - 在/save指令时，我采用了一个比较笨的方法，就是每次存之前都要先读一遍`save.json`,因为这样才能保证格式。想了下，有两个改进方法：
    - 打开`save.json`文件时，移动指针到倒二行，在之后写入文件
    - 使用数据库
  - 在/send指令中，我希望设计成：用户有两种选择，直接输出所存储的信息或发送save.json文件，刚开始我看的是[conversationbot.py](https://docs.python-telegram-bot.org/en/stable/examples.conversationbot.html),所以思路是通过ConversationHandler来实现，但是这样的话其实相当于设置快捷键，让用户点击输入信息到对话中，因此会影响到gpt接口的功能，虽然也有解决方法，就是设置正则，选择以message和file开头的，但是这样比较丑陋，所以我采用了另一种方式。
  - 第二种方式是inlinekeyboard，在判断后调用相关函数时没绕过来，开始的时候是照着例子里写的，但后来根据实际情况，写成`await send_file(update,context)await send_file(update,context)`,就好了
- 3月23日，尝试配置docker-compose，遇到两个问题：
  - 和之前一样，还是在网络问题上耽搁最久。最终解决方法是配置了
    ```
      environment:
        - http_proxy=http://172.17.0.1:7890
        - https_proxy=http://172.17.0.1:7890
    ```
  但这与我上次的解决方式不同，而且值得一提的是，我尝试删除`- https_proxy=http://172.17.0.1:7890`一栏，但运行不成功。
  - 挂载volume，这比较顺利，但实际运行出现了问题，通过报错信息排查后发现了问题是：我在文件夹中新建了`save.json`,但这是空的，而我的代码里只判断了该文件是否存在，当其存在时，默认其中是有内容的。添加一个判断即可。
- 4月18日，做了这几件事：
  - openAI注册账号时送的余额过期了，所以就注释掉了相关代码
  - 将bot.py挂载出来，这样以后在不需要额外依赖的时候就可以不用重新更新容器了。
  - 添加了新指令`/poetry`,使用的是`https://v1.jinrishici.com/all`的api。可以发送随机的一句古诗词名句
  - 修改了日志的配置，之前日志储存有些问题(在本地调试后要使用docker部署在服务器时创建了一个warning.json文件夹。排查后发现是我的docker-compose.yml文件写错了。*发现修改docker-compose.yml后需删除镜像，并重新拉取*)
- 4月19日，添加了新指令`\en_poetry` : 发送一首随机的英文诗
  在找api的时候花了些时间，刚开始找的是[https://www.poetry.com/poetry_api.php](https://www.poetry.com/poetry_api.php),但填写使用申请后没有回复。
  
  然后看到了[Poems API](https://poems.one/api/poem/#),它的页面做的比较精美，但文档之类的做得不是太完善。
  
  最后使用的是[PoetryDB](https://poetrydb.org/index.html)。免费，可供选择的选项多，接口文档也很完善，感谢这个项目。

  另外，我本来是打算将古诗和英文诗指令合起来，然后再随机输出的。但现在觉得分开来的话还是比较好点。译文方面还没找到比较好的库，又不愿意用机翻的，就暂且搁置，随缘吧。
- 4月28日 我前几天是使用crontab来定时运行重启的脚本。但没有效果。开始的时候我以为是我命令没有设置好，就在脚本里加了一行`date >> restart.txt`,使其每次运行都会打印日期到restart.txt里。却发现这个脚本是有在运行的。后来看`/var/spool/mail`里的报错信息才找到问题所在。报错信息是这样的`docker-compose: command not found`。问了Claude后才知道这是因为crontab运行的环境并不包含docker-compose命令,需要对路径进行指定。最终将脚本修改成如下即可。
  ```bash
  # restart FayeBot3.0
  cd /usr/local/project/telegramBot/Faye_Bot3.0/
  PATH=$PATH:/usr/local/bin/
  docker-compose restart  
  docker-compose logs
  date >> restart.txt
  ```
- 5月2日，由于我保存的文字已经有一定数量了，导致send_message阅读比较困难，所以有了添加分页选择的需求。通过学习示例代码，勉强把功能实现了。但代码写得很丑陋，没有做到代码的复用。一时没想到怎么去优化。先搁置吧。(似乎用ConversationHandler会好些)
---

## 学到的东西
### python
- 配置文件的读取
  ```python
    import json
    with open(config_path,'r') as f:
        config = json.load(f)
    
    proxy_url = config['proxy_url'] 
    token = config['token'] 
  ```

- 文件工作路径
  我的[bot.py](bot1.py)文件是存放在telegramBots这个文件夹中的，所以我就认为它的工作路径也就是这个文件夹，但出bug后发现是他的父文件夹
  ```python
  import os
  # 当前工作路径
  print(os.getcwd()) #D:\PythonLearning

  config_path = os.path.join(os.path.dirname(__file__),'config.json')
  ```
- 导出当前环境依赖包信息
  `pip freeze > requirements.txt`

- python 虚拟环境
  ```
  #新建
  python -m venv {环境名}
  ```
- json文件的读写
  ```python
  import json

  #写入
  with open(save_path,"a",encoding='utf-8') as f:
    f.write(json.dumps(data,ensure_ascil=False,indent=2))
    f.write('\n')

  #读取
  with open(save_path,'r',encoding='utf-8') as f:
    data = json.load(f)
    messages =[]
    for idx, obj in enumerate(data):
        messages.append(f"{idx+1}. {obj['text']}")
    if messages:
        message = "\n".join(messages)

  #内容判断是否为空
  file_size = os.stat(save_path).st_size
  if file_size == 0:
    print("file is empty")
  ```
- 日志的设置
  ```python
  # 日志的配置
  logger = logging.getLogger(__name__)
  logging.basicConfig(
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      level=logging.INFO,
  )
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') 

  file_handler = logging.FileHandler(filename=warning_path,mode='a',encoding='utf-8')
  file_handler.setFormatter(formatter)
  file_handler.setLevel(logging.INFO)

  stream_handler = logging.StreamHandler(sys.stdout)
  stream_handler.setFormatter(formatter)  
  stream_handler.setLevel(logging.WARNING)

  logger.addHandler(stream_handler)
  logger.addHandler(file_handler)
  ```
- 字符串的拼接
  `f_line = '\n'.join(lines)`

## Dokcker
- Docker的配置文件，Windows下的路径为：`C:\Users\{username}\.docker\daemon.json`

- Docker的基本使用
  ```docker
  # 将build好的image上传到docker hub
  docker login -u $username
  docker tag $imagename $username/$imagename
  docker push $username/$imagename

  # 查看运行的container
  docker ps
  
  # 查看所有的container
  docker ps -a
  
  # 查看container的配置情况
  docker inspect container-name

  # 查看容器的日志
  docker logs container-name
  
  # 删除容器
  docker rm container-name

  # 删除镜像
  docker rmi imagename

  # 查看所有的container
  ```

## python-telegram-bot
- inlineKeyboard 的使用
  - `keyboard = [[InlineKeyboardButton(f"{i}", callback_data=str(i)) for i in range(1, real_pages+1)]]`
  - 
- CallbackQuery. 
  - 每个CallbackQuery都会去响应符合pattern的query.
  - `update.callback_query.edit_message_text` 是修改发起CallbackQuery的那条。

## 参考
- [inlinekeyboard.py](https://docs.python-telegram-bot.org/en/stable/examples.inlinekeyboard.html)
- [conversationbot.py](https://docs.python-telegram-bot.org/en/stable/examples.conversationbot.html)
- [errorhandlerbot.py](https://docs.python-telegram-bot.org/en/stable/examples.errorhandlerbot.html)
- [CallbackQuery](https://docs.python-telegram-bot.org/en/stable/telegram.callbackquery.html)
- [get_up.py](https://github.com/yihong0618/2023/blob/639e3ac9c9982edaee1481489ccd4d56b43e52f8/get_up.py)
- [yihong0618/tg_bing_dalle: tg bing dalle-3](https://github.com/yihong0618/tg_bing_dalle/tree/main)