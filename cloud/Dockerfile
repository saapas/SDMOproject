# Build context is the repo root (see docker-compose.yml)
FROM python:3.12-slim
WORKDIR /app
COPY cloud/requirements.txt .
RUN pip install -r requirements.txt
COPY cloud/ cloud/
CMD ["uvicorn", "cloud.cloud:app", "--host", "0.0.0.0", "--port", "8000"]
