FROM python:3.10.6
# ENV http_proxy=http://127.0.0.1:7890
# ENV https_proxy=https://127.0.0.1:7890
WORKDIR /app
COPY . . 
RUN pip install -r requirements.txt
CMD ["python", "bot1.py"]