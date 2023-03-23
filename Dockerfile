FROM python:3.10.6
# ENV HTTP_PROXY="http://172.17.0.1:7890"
# ENV httpporxy="http://172.17.0.1:7890"
# ENV https_proxy=https://127.0.0.1:7890
WORKDIR /app
COPY .dockerignore .
COPY . . 
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]