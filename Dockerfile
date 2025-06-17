FROM python:3-slim
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["python3", "server.py", "config.yml"]