# Build context is the repo root (see docker-compose.yml)
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 app
WORKDIR /app
COPY device/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/ common/
COPY device/ device/
USER app
CMD ["python", "-m", "device.device"]
