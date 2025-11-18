FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs

EXPOSE 8080

ENV BIND=0.0.0.0
ENV PORT=8080

CMD ["python", "-m", "uvicorn", "app.main:sio_app", "--host", "0.0.0.0", "--port", "8080"]
