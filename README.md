# AI-MVP Speech Service

AI destekli İngilizce öğrenme platformu için TTS (Text-to-Speech) ve STT (Speech-to-Text) servisi.

## Özellikler

- 🎤 **TTS (Text-to-Speech)**: Kokoro modeli ile doğal ses üretimi
- 🎧 **STT (Speech-to-Text)**: Faster-Whisper ile hızlı ses tanıma
- ⚡ **FastAPI**: Yüksek performanslı REST API
- 🐳 **Docker**: Kolay deployment

## API Endpoints

### Health Check
```
GET /
```

### Text-to-Speech
```
POST /tts?text=Hello&voice=af_heart&speed=0.9
```

**Parametreler:**
- `text`: Dönüştürülecek metin
- `voice`: Ses modeli (af_heart, af_sky, af_bella)
- `speed`: Konuşma hızı (0.5-2.0)

**Response:** WAV audio file

### Speech-to-Text
```
POST /stt?language=en
```

**Body:** Audio file (multipart/form-data)

**Response:**
```json
{
  "text": "transcribed text",
  "segments": [...],
  "duration": 5.2,
  "compute_time": 1.3,
  "rtf": 4.0
}
```

## Lokal Çalıştırma
```bash
# Virtual environment
python -m venv venv
venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r app/requirements.txt

# Servisi başlat
cd app
python main.py
```

Servis `http://localhost:8000` adresinde çalışacak.

## Railway Deployment

1. Railway projesine git
2. "Deploy from GitHub repo" seç
3. Repo'yu bağla
4. Otomatik deploy başlayacak

## Model Bilgileri

- **TTS Model**: Kokoro-82M (hexgrad/Kokoro-82M)
- **STT Model**: Faster-Whisper Base
- **Compute**: CPU optimized (int8)
```

---

## ✅ Dosya Yapısı Kontrolü

Şu yapıya sahip olmalısın:
```
ai-mvp-speech-service/
├── Dockerfile
├── .dockerignore
├── railway.json
├── README.md
└── app/
    ├── main.py
    ├── requirements.txt
    ├── .gitignore
    ├── tts/
    │   ├── __init__.py
    │   └── tts_service.py
    └── stt/
        ├── __init__.py
        └── stt_service.py