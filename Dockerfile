FROM python:3-slim
WORKDIR /app
COPY . .

RUN apt update && apt install libcap-dev -y

RUN pip install -r requirements.txt

RUN mkdir data

CMD ["python3", "-u", "server.py", "data/config.yml"]