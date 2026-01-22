# AI-MVP Speech Service

AI destekli İngilizce öğrenme platformu için TTS (Text-to-Speech) ve STT (Speech-to-Text) servisi.

##  Özellikler

-  **TTS (Text-to-Speech)**: Piper modeli ile doğal ses üretimi
-  **STT (Speech-to-Text)**: Faster-Whisper ile hızlı ses tanıma
-  **FastAPI**: Yüksek performanslı REST API
-  **Lazy Loading**: Modeller ilk istekte yüklenir (hızlı başlatma)
-  **Docker**: Kolay deployment
-  **CORS**: Frontend entegrasyonu için hazır

##  Canlı URL

```
https://ai-mvp-speech-service-production.up.railway.app
```

## API Endpoints

### Health Check
```bash
GET /
```

**Response:**
```json
{
  "status": "ok",
  "message": "AI-MVP Speech Service is running",
  "tts_ready": false,
  "stt_ready": false,
  "endpoints": {
    "tts": "/tts",
    "stt": "/stt"
  }
}
```

### Text-to-Speech
```bash
POST /tts?text=Hello%20world&voice=en_US-lessac-medium&speed=1.0
```

**Parametreler:**
- `text` (required): Dönüştürülecek metin
- `voice` (optional): Ses modeli (varsayılan: en_US-lessac-medium)
- `speed` (optional): Konuşma hızı 0.5-2.0 (varsayılan: 1.0)

**Response:** WAV audio file (16-bit, 22050Hz, Mono)

**Örnek:**
```bash
curl -X POST "https://ai-mvp-speech-service-production.up.railway.app/tts" \
  -d "text=Hello world&speed=1.0" \
  -o speech.wav
```

### Speech-to-Text
```bash
POST /stt?language=en
```

**Body:** Audio file (multipart/form-data)

**Response:**
```json
{
  "text": "Hello, how are you today?",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello, how are you today?"
    }
  ],
  "duration": 2.5,
  "compute_time": 0.8,
  "rtf": 3.12,
  "language": "en",
  "language_probability": 0.98
}
```

**Örnek:**
```bash
curl -X POST "https://ai-mvp-speech-service-production.up.railway.app/stt?language=en" \
  -F "audio=@recording.wav"
```

## Lokal Çalıştırma

```bash
# Virtual environment oluştur
cd ai-mvp-speech-service/app
python -m venv venv

# Aktive et
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Servisi başlat
python main.py
```

Servis `http://localhost:8000` adresinde çalışacak.

**Swagger UI:** `http://localhost:8000/docs`

##  Railway Deployment

1. Railway.app → Sign in with GitHub
2. "New Project" → "Deploy from GitHub repo"
3. Repository seç: `ai-mvp-speech-service`
4. Railway otomatik Dockerfile'ı algılayacak
5. "Deploy" tıkla
6. Settings → Networking → "Generate Domain"

**Build Süresi:** ~3-5 dakika

## Dosya Yapısı

```
ai-mvp-speech-service/
├── Dockerfile              # Docker container tanımı
├── .dockerignore          # Docker build'de ignore edilecekler
├── .gitignore             # Git'te ignore edilecekler
├── README.md              # Bu dosya
└── app/                   # Uygulama kodu
    ├── main.py            # FastAPI app (entry point)
    ├── requirements.txt   # Python dependencies
    ├── tts/               # TTS modülü
    │   ├── __init__.py
    │   └── tts_service.py # Piper TTS servisi
    └── stt/               # STT modülü
        ├── __init__.py
        └── stt_service.py # Faster-Whisper servisi
```

## Teknoloji Stack

**Backend:**
- FastAPI 0.115.5
- Python 3.10
- Uvicorn (ASGI server)

**TTS:**
- Piper TTS v1.2.0
- Voice: en_US-lessac-medium
- Format: WAV (16-bit, 22050Hz, Mono)
- Memory: ~150-200MB

**STT:**
- Faster-Whisper (tiny model)
- CTranslate2 (CPU optimized)
- Compute: int8 quantization
- Memory: ~100MB

**Deployment:**
- Platform: Railway.app
- Container: Docker
- Plan: Free Tier (512MB RAM)


