FROM python:3-slim
WORKDIR /app
COPY . .

RUN pip install requests argon2-cffi pyyaml cloudflare

CMD ["python3", "server.py", "config.yml"]