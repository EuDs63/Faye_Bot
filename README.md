# README

## 介绍
基于python的telegram bot，现支持功能
- /dog 返回一张随机的狗的照片
- 通过api接入了ChatGPT，支持直接对话

## ToDo
- [ ] 完善Dockerfile，docker-compose的配置
- [ ] 完善日志设置，保存聊天记录 
- [ ] 修改代码，现在似乎是会不断把之前的记录叠加？



## 部署
```
docker build -t fayebot .
# Windows系统
# docker run --e httpproxy="http://host.docker.internal:7890" fayebot 
# Linux 系统
docker run --e httpproxy="http://172.17.0.1:7890" fayebot
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
  - 尝试在run image时添加命令，如`docker run --e httpproxy="http://172.17.0.1:7890" fayebot`，成功了，但发现若配置了httpsproxy则不行，未知其因。
## 学到的东西
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
- logger

-Docker的配置文件，Windows下的路径为：`C:\Users\{username}\.docker\daemon.json`

