# Build context is the repo root (see docker-compose.yml)
FROM python:3.12-slim
WORKDIR /app
COPY device/requirements.txt .
RUN pip install -r requirements.txt
COPY common/ common/
COPY device/ device/
CMD ["python", "-m", "device.device"]
