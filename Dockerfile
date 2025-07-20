FROM python:3.12-slim AS builder

RUN apt update && apt install libcap-dev gcc -y

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY . .

COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12

RUN mkdir data

CMD ["python3", "-u", "server.py", "data/config.yml"]