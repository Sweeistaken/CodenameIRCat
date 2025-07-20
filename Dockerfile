FROM python:3.12-slim AS builder

RUN apt update && apt install libcap-dev gcc -y

RUN pip install -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY . .

COPY --from builder /usr/lib/python3.12 /usr/lib/python3.12

RUN mkdir data

CMD ["python3", "-u", "server.py", "data/config.yml"]