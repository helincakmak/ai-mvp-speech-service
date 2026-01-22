from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import io

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI-MVP Speech Service",
    description="TTS (Kokoro) ve STT (Faster-Whisper) servisi",
    version="1.0.0",
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servis referansları (modeller henüz yüklenmiyor - lazy-load)
tts_service = None
stt_service = None


def get_tts_service():
    """
    Kokoro TTS servisini lazy-load eder.
    İlk çağrıldığında modeli yükler, sonra aynı instance'ı kullanır.
    """
    global tts_service
    if tts_service is None:
        logger.info("📦 TTS servisi ilk kez yükleniyor (lazy-load, modeller indirilecek)...")
        from tts.tts_service import TTSService  # asıl yük TTSService içinde

        tts_service = TTSService()
        logger.info("✅ TTS servisi hazır!")
    return tts_service


def get_stt_service():
    """
    Faster-Whisper STT servisini lazy-load eder.
    İlk çağrıldığında modeli yükler, sonra aynı instance'ı kullanır.
    """
    global stt_service
    if stt_service is None:
        logger.info("📦 STT servisi ilk kez yükleniyor (lazy-load, modeller indirilecek)...")
        from stt.stt_service import STTService

        # deneme için en küçük model: tiny
        stt_service = STTService(model_size="tiny")
        logger.info("✅ STT servisi hazır!")
    return stt_service


@app.on_event("startup")
async def startup_event():
    # Artık burada ağır model yükleme yok,
    # sadece servis lazy-load kullanılacağını logluyoruz.
    logger.info("🚀 Servis başlatılıyor (modeller lazy-load edilecek).")


# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "AI-MVP Speech Service is running",
        "tts_ready": tts_service is not None,
        "stt_ready": stt_service is not None,
        "endpoints": {
            "tts": "/tts",
            "stt": "/stt",
        },
    }


# TTS endpoint
@app.post("/tts")
async def text_to_speech(
    text: str,
    voice: str = "af_heart",
    speed: float = 0.9,
):
    try:
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Metin boş olamaz")

        # Lazy-load TTS (ilk istekte modeli yükler)
        service = get_tts_service()

        logger.info(f"📝 TTS isteği: text='{text[:50]}...', voice={voice}, speed={speed}")

        audio_bytes = service.text_to_speech(text, voice=voice, speed=speed)

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=speech.wav",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ TTS hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# STT endpoint
@app.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = "en",
):
    try:
        # Lazy-load STT (ilk istekte modeli yükler)
        service = get_stt_service()

        logger.info(f"🎤 STT isteği: filename={audio.filename}, language={language}")

        audio_bytes = await audio.read()
        result = service.speech_to_text(audio_bytes, language=language)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ STT hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Lokal geliştirme için (Railway Docker CMD kullanıyor)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
