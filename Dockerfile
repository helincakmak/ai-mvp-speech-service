FROM python:3.10-slim

WORKDIR /app

# Sistem paketleri
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Requirements önce kopyala (cache için)
COPY app/requirements.txt .

# Tek seferde yükle
RUN pip install --no-cache-dir \
    fastapi==0.115.5 \
    uvicorn[standard]==0.32.1 \
    python-multipart==0.0.20 \
    numpy==1.26.4 \
    && pip install --no-cache-dir \
    kokoro \
    faster-whisper==1.1.0 \
    && pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && rm -rf /root/.cache/pip

# App kopyala
COPY app/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]