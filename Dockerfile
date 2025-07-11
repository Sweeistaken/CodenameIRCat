FROM python:3-slim
WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

RUN mkdir data

CMD ["python3", "-u", "server.py", "data/config.yml"]