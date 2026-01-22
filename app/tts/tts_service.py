import io
import wave
import logging
from piper import PiperVoice

logger = logging.getLogger(__name__)


class TTSService:
    def __init__(self):
        """
        Piper TTS modelini yükle.
        Railway free plan için optimize edilmiş hafif model kullanıyoruz.
        """
        try:
            logger.info("🎤 Piper TTS yükleniyor...")
            
            # Hafif İngilizce model (en_US-lessac-medium)
            # Model otomatik indirilecek (~50MB)
            self.voice = PiperVoice.load(
                model_path=None,  # Otomatik indir
                config_path=None,
                use_cuda=False  # Railway'de GPU yok
            )
            
            logger.info("✅ Piper TTS başarıyla yüklendi!")
            
        except Exception as e:
            logger.error(f"❌ Piper TTS yüklenirken hata: {e}")
            raise

    def text_to_speech(
        self,
        text: str,
        voice: str = "en_US-lessac-medium",  # Model adı
        speed: float = 1.0,
    ) -> bytes:
        """
        Metni sese çevir.
        
        Args:
            text: Dönüştürülecek metin
            voice: Ses modeli (şimdilik sabit)
            speed: Konuşma hızı (0.5-2.0)
        
        Returns:
            WAV formatında ses verisi (bytes)
        """
        try:
            if not text or not text.strip():
                raise ValueError("Metin boş olamaz")

            logger.info(f"🎤 Piper TTS: '{text[:50]}...'")
            logger.info(f"Speed: {speed}")

            # Piper ile ses üret
            audio_stream = io.BytesIO()
            
            # Synthesize
            with wave.open(audio_stream, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(22050)  # Piper default
                
                # Generate audio
                for audio_bytes in self.voice.synthesize_stream_raw(
                    text,
                    length_scale=1.0/speed  # Piper'da speed tersten çalışır
                ):
                    wav_file.writeframes(audio_bytes)
            
            # Get bytes
            audio_stream.seek(0)
            result = audio_stream.getvalue()
            
            logger.info(f"✅ TTS başarılı! Boyut: {len(result)} bytes")
            return result

        except Exception as e:
            logger.error(f"❌ TTS hatası: {e}")
            raise