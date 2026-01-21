FROM python:3.10-slim

WORKDIR /app

# Sistem bağımlılıkları (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python paketleri
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Uygulama kodları
COPY app/ .

# Port
EXPOSE 8000

# Başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]