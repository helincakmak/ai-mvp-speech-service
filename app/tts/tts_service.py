import io
import wave
import logging
from pathlib import Path

from piper import PiperVoice
from piper.download import get_voices, ensure_voice_exists, find_voice

logger = logging.getLogger(__name__)

# Piper için kullanılacak ses adı (Piper voices listesinde var)
DEFAULT_VOICE_NAME = "en_US-lessac-medium"

# Modellerin indirileceği klasör
VOICES_DIR = Path("/app/piper_voices")


class TTSService:
    def __init__(self, voice_name: str = DEFAULT_VOICE_NAME):
        """
        Piper TTS modelini yükler.
        - Railway free plan için hafif bir İngilizce model (en_US-lessac-medium) kullanıyoruz.
        - Model yoksa piper.download ile HuggingFace'ten indirir.
        """
        try:
            logger.info("🎤 Piper TTS yükleniyor...")
            VOICES_DIR.mkdir(parents=True, exist_ok=True)

            # İndirilebilir voice listesi
            voices_info = get_voices(download_dir=VOICES_DIR, update_voices=False)

            # Model dosyaları yoksa indir
            ensure_voice_exists(
                name=voice_name,
                data_dirs=[VOICES_DIR],
                download_dir=VOICES_DIR,
                voices_info=voices_info,
            )

            # İndirilen model + config path'lerini bul
            model_path, config_path = find_voice(
                name=voice_name,
                data_dirs=[VOICES_DIR],
            )

            logger.info(f"🔎 Piper modeli: {model_path}, config: {config_path}")

            # Voice yükle (sadece CPU)
            self.voice = PiperVoice.load(
                model_path=str(model_path),
                config_path=str(config_path),
                use_cuda=False,
            )

            # Sample rate'i config'ten al
            self.sample_rate = self.voice.config.sample_rate
            logger.info(
                f"✅ Piper TTS hazır! sample_rate={self.sample_rate}, voice={voice_name}"
            )

        except Exception as e:
            logger.error(f"❌ Piper TTS yüklenirken hata: {e}")
            raise

    def text_to_speech(
        self,
        text: str,
        voice: str = DEFAULT_VOICE_NAME,  # Şimdilik tek voice, parametre frontend için
        speed: float = 1.0,
    ) -> bytes:
        """
        Metni sese çevir.

        Args:
            text: Dönüştürülecek metin.
            voice: Şimdilik sabit model (en_US-lessac-medium).
            speed: Konuşma hızı (0.5 - 2.0). 1.0 = normal.

        Returns:
            WAV formatında ses verisi (bytes).
        """
        try:
            text = (text or "").strip()
            if not text:
                raise ValueError("Metin boş olamaz")

            logger.info(f"🎤 Piper TTS: '{text[:80]}...' speed={speed}")

            # Piper'da length_scale > 1 yavaşlatır, < 1 hızlandırır.
            # Hissi korumak için speed'i ters çeviriyoruz.
            if speed <= 0:
                speed = 1.0
            length_scale = max(0.25, min(2.0, 1.0 / speed))

            audio_stream = io.BytesIO()

            # wave container'ı memory içinde aç
            with wave.open(audio_stream, "wb") as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit PCM
                wav_file.setframerate(self.sample_rate)

                # Piper kendi içinde int16 üretip wav_file'a yazar
                self.voice.synthesize(
                    text,
                    wav_file,
                    length_scale=length_scale,
                )

            audio_stream.seek(0)
            result = audio_stream.getvalue()
            logger.info(f"✅ TTS başarılı! Boyut={len(result)} bytes")

            return result

        except Exception as e:
            logger.error(f"❌ TTS hatası: {e}")
            raise
