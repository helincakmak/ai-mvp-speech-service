from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from tts.tts_service import TTSService
from stt.stt_service import STTService  # ✅ EKLENDI
import io

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="AI-MVP Speech Service",
    description="TTS (Kokoro) ve STT (Faster-Whisper) servisi",
    version="1.0.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servisler
tts_service = None
stt_service = None  # ✅ EKLENDI

@app.on_event("startup")
async def startup_event():
    global tts_service, stt_service  # ✅ Güncellendi
    logger.info("🚀 Servis başlatılıyor...")
    
    # TTS yükle
    tts_service = TTSService()
    logger.info("✅ TTS servisi hazır!")
    
    # STT yükle
    stt_service = STTService(model_size="base")  # ✅ EKLENDI
    logger.info("✅ STT servisi hazır!")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "AI-MVP Speech Service is running",
        "endpoints": {
            "tts": "/tts",
            "stt": "/stt"
        }
    }

# TTS endpoint
@app.post("/tts")
async def text_to_speech(
    text: str,
    voice: str = "af_heart",
    speed: float = 0.9
):
    """
    Metin → Ses dönüştürme
    """
    try:
        if not tts_service:
            raise HTTPException(status_code=503, detail="TTS servisi henüz hazır değil")
        
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Metin boş olamaz")
        
        logger.info(f"📝 TTS isteği: text='{text[:50]}...', voice={voice}, speed={speed}")
        
        audio_bytes = tts_service.text_to_speech(text, voice=voice, speed=speed)
        
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/wav",
            headers={
                "Content-Disposition": f"attachment; filename=speech.wav"
            }
        )
        
    except Exception as e:
        logger.error(f"❌ TTS hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# STT endpoint (✅ GERÇEK)
@app.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = "en"
):
    """
    Ses → Metin dönüştürme
    
    Args:
        audio: Ses dosyası (WAV, MP3, vb.)
        language: Dil kodu (en, tr, vb.)
    """
    try:
        if not stt_service:
            raise HTTPException(status_code=503, detail="STT servisi henüz hazır değil")
        
        logger.info(f"🎤 STT isteği: filename={audio.filename}, language={language}")
        
        # Audio dosyasını oku
        audio_bytes = await audio.read()
        
        # STT işlemi
        result = stt_service.speech_to_text(audio_bytes, language=language)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ STT hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Server başlatma
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )