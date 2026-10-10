# Build context is the repo root (see docker-compose.yml)
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 app && mkdir /data && chown app:app /data
WORKDIR /app
COPY cloud/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY cloud/ cloud/
USER app
CMD ["uvicorn", "cloud.cloud:app", "--host", "0.0.0.0", "--port", "8000"]
