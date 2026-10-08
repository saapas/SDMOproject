# Build context is the repo root (see docker-compose.yml)
FROM python:3.12-slim
WORKDIR /app
COPY gateway/requirements.txt .
RUN pip install -r requirements.txt
COPY common/ common/
COPY gateway/ gateway/
CMD ["uvicorn", "gateway.gateway:app", "--host", "0.0.0.0", "--port", "8080"]
