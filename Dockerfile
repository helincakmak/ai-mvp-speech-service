# Temel Python imajı
FROM python:3.10-slim

# Python çıktıları buffer'lanmasın, .pyc üretmesin
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Çalışma dizini
WORKDIR /app

# Sistem paketleri (ffmpeg gerekiyor)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "torch==2.2.0" --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# Uygulama kodları
COPY app/ .

# Uygulama 8000 portunu dinleyecek
EXPOSE 8000

# Uvicorn ile FastAPI'yi başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
