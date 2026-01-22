import io
import wave
import logging

import numpy as np
import torch
from kokoro import KPipeline

logger = logging.getLogger(__name__)

SAMPLE_RATE = 24_000
FADE_MS = 40  # fade-in/out süresi (robotik ses önleme)


class TTSService:
    def __init__(self) -> None:
        """
        Kokoro TTS pipeline'ını yükler.
        Railway free planda GPU olmadığı için device doğrudan 'cpu'.
        Bu sınıf zaten main.py'de lazy-load edildiği için,
        sadece ilk /tts isteğinde çalışacak.
        """
        try:
            logger.info("Kokoro TTS yükleniyor...")

            # Railway'de GPU yok, doğrudan CPU kullanıyoruz
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Device: {device}")

            self.pipeline = KPipeline(
                lang_code="a",            # İngilizce
                repo_id="hexgrad/Kokoro-82M",
                device=device,
            )

            logger.info("✅ Kokoro TTS başarıyla yüklendi!")

        except Exception as e:
            logger.error(f"❌ Kokoro TTS yüklenirken hata: {e}")
            raise

    def text_to_speech(
        self,
        text: str,
        voice: str = "af_heart",
        speed: float = 0.9,
    ) -> bytes:
        """
        Metni sese çevirir.

        Args:
            text: Dönüştürülecek metin
            voice: Ses modeli (af_heart, af_sky, af_bella, am_adam vb.)
            speed: Konuşma hızı (0.5–2.0 arası, varsayılan 0.9)

        Returns:
            WAV formatında ses verisi (bytes)
        """
        try:
            if not text or not text.strip():
                raise ValueError("Metin boş olamaz.")

            logger.info(f"🎤 TTS işlemi başlıyor: '{text[:50]}...'")
            logger.info(f"Voice: {voice}, Speed: {speed}")

            # Kokoro ile ses üret
            gen = self.pipeline(
                text,
                voice=voice,
                speed=speed,
            )

            # Tüm chunk'ları birleştir
            audio_chunks = []
            for _, _, audio in gen:
                audio_chunks.append(np.asarray(audio, dtype=np.float32))

            if not audio_chunks:
                raise ValueError("Ses üretilemedi!")

            # Chunk'ları tek array'e birleştir
            audio = np.concatenate(audio_chunks)

            # Fade-in/out uygula (robotik hissi azaltır)
            audio = self._apply_fade(audio)

            # WAV bytes'a çevir
            audio_bytes = self._numpy_to_wav(audio, SAMPLE_RATE)

            audio_duration = len(audio) / SAMPLE_RATE
            logger.info(
                f"✅ TTS başarılı! Ses boyutu: {len(audio_bytes)} bytes, "
                f"Süre: {audio_duration:.2f}s"
            )

            return audio_bytes

        except Exception as e:
            logger.error(f"❌ TTS hatası: {e}")
            raise

    def _apply_fade(self, audio: np.ndarray) -> np.ndarray:
        """
        Başına ve sonuna fade-in/out uygular (sert giriş/çıkışı yumuşatır).
        """
        audio = audio.astype(np.float32)
        n = int(SAMPLE_RATE * FADE_MS / 1000)
        n = max(1, min(n, len(audio) // 2))

        fade_in = np.linspace(0.0, 1.0, n, dtype=np.float32)
        fade_out = fade_in[::-1]

        audio[:n] *= fade_in
        audio[-n:] *= fade_out
        return audio

    def _numpy_to_wav(self, samples: np.ndarray, sample_rate: int) -> bytes:
        """
        NumPy array'i WAV bytes'a çevirir.
        """
        # Float32'den Int16'ya çevir
        audio_int16 = (samples * 32767).astype(np.int16)

        # WAV dosyasını memory'de oluştur
        wav_io = io.BytesIO()
        with wave.open(wav_io, "wb") as wav_file:
            wav_file.setnchannels(1)   # Mono
            wav_file.setsampwidth(2)   # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_int16.tobytes())

        return wav_io.getvalue()
