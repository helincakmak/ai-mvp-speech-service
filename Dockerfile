FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Sistem paketleri
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Requirements
COPY app/requirements.txt .

# Önce pip + CPU Torch, sonra diğer paketler
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "torch==2.2.0" --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip

# App kodlarını kopyala
COPY app/ .

EXPOSE 8000

# Python ile PORT'u al
CMD python -c "import os; os.system(f\"uvicorn main:app --host 0.0.0.0 --port {os.getenv('PORT', '8000')}\")"