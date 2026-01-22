# Temel Python imajı
FROM python:3.10-slim

# Python çıktıları buffer'lanmasın, .pyc üretilmesin
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Çalışma dizini
WORKDIR /app

# Sistem paketleri (ffmpeg + espeak-ng Piper için gerekli)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını yükle
COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Uygulama kodları
COPY app/ .

# Piper modelleri için klasör (isteğe bağlı)
RUN mkdir -p /app/piper_voices

# Uygulama 8000 portunu dinleyecek
EXPOSE 8000

# Uvicorn ile FastAPI'yi başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
