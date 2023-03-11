FROM python:3.10.6
WORKDIR /app
COPY . . 
RUN pip install -r requirements.txt
CMD ["python", "bot1.py"]