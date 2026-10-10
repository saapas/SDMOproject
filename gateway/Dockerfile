# Build context is the repo root (see docker-compose.yml)
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 app
WORKDIR /app
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common/ common/
COPY gateway/ gateway/
USER app
CMD ["uvicorn", "gateway.gateway:app", "--host", "0.0.0.0", "--port", "8080"]
