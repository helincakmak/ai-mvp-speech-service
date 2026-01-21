FROM python:3.10-slim

WORKDIR /app

# Sistem paketleri
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Requirements
COPY app/requirements.txt .

# Paketleri yükle (modeller YOK, sadece kütüphaneler)
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# App kodlarını kopyala
COPY app/ .

EXPOSE 8000

# Modeller ilk çalıştırmada indirilecek
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]