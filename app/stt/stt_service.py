from faster_whisper import WhisperModel
import logging
import time
import tempfile
import os

logger = logging.getLogger(__name__)


class STTService:
    def __init__(self, model_size: str = "tiny"): 
        """
        Faster-Whisper STT modelini yükle
        
        Args:
            model_size: tiny, base, small, medium, large
        """
        try:
            logger.info(f"🎧 Faster-Whisper STT yükleniyor... (model: {model_size})")
            
            t0 = time.time()
            
            # CPU için optimize edilmiş
            self.model = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8"  # Hızlı çalışması için
            )
            
            t1 = time.time()
            logger.info(f"✅ Whisper STT yüklendi! Süre: {t1-t0:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Whisper STT yüklenirken hata: {e}")
            raise
    
    def speech_to_text(self, audio_bytes: bytes, language: str = "en") -> dict:
        """
        Sesi metne çevir
        
        Args:
            audio_bytes: Ses dosyası (bytes)
            language: Dil kodu (en, tr, vb.)
        
        Returns:
            {
                "text": "tam metin",
                "segments": [...],
                "duration": 5.2,
                "compute_time": 1.3,
                "rtf": 4.0
            }
        """
        try:
            # Geçici dosya oluştur (Whisper dosya bekliyor)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name
            
            logger.info(f"🎧 STT işlemi başlıyor... (language: {language})")
            
            t_start = time.time()
            
            # Transcribe
            segments, info = self.model.transcribe(
                tmp_path,
                language=language,
                beam_size=5,
                vad_filter=True  # Sessiz kısımları atla
            )
            
            # Segmentleri topla
            segment_list = []
            full_text = []
            
            for seg in segments:
                segment_list.append({
                    "start": round(seg.start, 2),
                    "end": round(seg.end, 2),
                    "text": seg.text.strip()
                })
                full_text.append(seg.text.strip())
            
            t_end = time.time()
            
            # Temizlik
            os.unlink(tmp_path)
            
            duration = info.duration
            compute_time = t_end - t_start
            rtf = duration / compute_time if compute_time > 0 else 0
            
            result = {
                "text": " ".join(full_text),
                "segments": segment_list,
                "duration": round(duration, 2),
                "compute_time": round(compute_time, 2),
                "rtf": round(rtf, 2),
                "language": info.language,
                "language_probability": round(info.language_probability, 2)
            }
            
            logger.info(f"✅ STT başarılı! RTF: {rtf:.2f}, Text: '{result['text'][:50]}...'")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ STT hatası: {e}")
            # Temizlik (hata durumunda)
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise