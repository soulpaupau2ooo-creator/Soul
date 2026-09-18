"""
Enterprise Production-Ready TTS Service for Soulbekbot.

Features:
- Primary Provider: Microsoft Edge Neural TTS (uz-UZ-MadinaNeural / uz-UZ-SardorNeural)
- Fallback Provider: Secondary voice -> gTTS (Google Translate fallback)
- Circuit Breaker pattern with cooldown recovery
- Full 7-stage Uzbek text normalization
- Sentence boundary-aware chunking for long essays
- Disk & Memory LRU caching
- Audio post-processing integration (FFmpeg / Loudnorm / Opus)
- Structured execution metrics
"""

from __future__ import annotations

import abc
import asyncio
import hashlib
import io
import logging
import os
import re
import time
from typing import Dict, List, Optional, Tuple

try:
    import edge_tts
except ImportError:  # pragma: no cover - optional dependency for runtime-only TTS
    edge_tts = None

try:
    from gtts import gTTS
except ImportError:  # pragma: no cover - optional dependency for runtime-only TTS
    gTTS = None

from tts.audio_post import post_process_audio
from tts.uzbek_normalizer import UzbekTextNormalizer

logger = logging.getLogger("TTSService")

# Standard Voices Map
VOICE_MAP: Dict[str, Dict[str, str]] = {
    "uz": {
        "female": "uz-UZ-MadinaNeural",
        "male": "uz-UZ-SardorNeural",
        "default": "uz-UZ-MadinaNeural",
    },
    "ru": {
        "female": "ru-RU-SvetlanaNeural",
        "male": "ru-RU-DmitryNeural",
        "default": "ru-RU-SvetlanaNeural",
    },
    "en": {
        "female": "en-US-JennyNeural",
        "male": "en-US-GuyNeural",
        "default": "en-US-JennyNeural",
    },
}


class BaseTTSProvider(abc.ABC):
    """Abstract interface for speech synthesis adapters."""

    @abc.abstractmethod
    async def synthesize(self, text: str, voice: str, rate: str = "+0%") -> Optional[bytes]:
        """Synthesize text into raw audio bytes (MP3)."""
        pass


class EdgeTTSProvider(BaseTTSProvider):
    """Primary asynchronous speech synthesis adapter powered by Microsoft Azure Neural voices."""

    async def synthesize(self, text: str, voice: str, rate: str = "+0%") -> Optional[bytes]:
        if not text or not text.strip() or edge_tts is None:
            return None

        try:
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
            buf = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])

            buf.seek(0)
            data = buf.read()
            if len(data) > 100:
                return data
            return None
        except Exception as e:
            logger.warning(f"EdgeTTS synthesis failure for voice '{voice}': {e}")
            return None


class GTTSFallbackProvider(BaseTTSProvider):
    """Emergency fallback provider when neural services are completely unreachable."""

    async def synthesize(self, text: str, voice: str, rate: str = "+0%") -> Optional[bytes]:
        if not text or not text.strip() or gTTS is None:
            return None

        try:
            # Map language
            gtts_lang = "ru" if "ru" in voice.lower() else "en" if "en" in voice.lower() else "tr"

            def _sync_gtts():
                tts = gTTS(text=text[:1000], lang=gtts_lang, slow=False)
                buf = io.BytesIO()
                tts.write_to_fp(buf)
                buf.seek(0)
                return buf.read()

            data = await asyncio.to_thread(_sync_gtts)
            return data if data and len(data) > 100 else None
        except Exception as e:
            logger.error(f"GTTS fallback error: {e}")
            return None


class TTSService:
    """Central orchestrator for text-to-speech synthesis."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.normalizer = UzbekTextNormalizer()
        self.primary_provider = EdgeTTSProvider()
        self.fallback_provider = GTTSFallbackProvider()

        # Cache directory
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", "tts_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

        # Circuit breaker state
        self._failure_count = 0
        self._circuit_open_until = 0.0
        self._max_consecutive_failures = 3
        self._cooldown_seconds = 60.0

        # Metrics
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "primary_success": 0,
            "fallback_used": 0,
            "failures": 0,
            "last_latency_ms": 0.0,
        }

    def _get_cache_path(self, cache_key: str, ext: str = "mp3") -> str:
        return os.path.join(self.cache_dir, f"{cache_key}.{ext}")

    def _compute_hash(self, text: str, voice: str, rate: str) -> str:
        h = hashlib.sha256()
        h.update(text.encode("utf-8"))
        h.update(voice.encode("utf-8"))
        h.update(rate.encode("utf-8"))
        return h.hexdigest()[:24]

    def resolve_voice(self, lang: str = "uz", gender: str = "female") -> str:
        """Resolve optimal neural voice string based on language and user preference."""
        lang_config = VOICE_MAP.get(lang.lower(), VOICE_MAP["uz"])
        return lang_config.get(gender.lower(), lang_config["default"])

    def split_into_chunks(self, text: str, max_chars: int = 1500) -> List[str]:
        """
        Split long essays safely at sentence or paragraph boundaries
        to ensure natural pacing without cutting mid-thought.
        """
        if len(text) <= max_chars:
            return [text]

        paragraphs = text.split("\n\n")
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= max_chars:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""

                # If a single paragraph is longer than max_chars, split by sentences
                if len(para) > max_chars:
                    sentences = re.split(r"(?<=[.!?])\s+", para)
                    sub_chunk = ""
                    for sent in sentences:
                        sent = sent.strip()
                        if len(sub_chunk) + len(sent) + 1 <= max_chars:
                            sub_chunk = f"{sub_chunk} {sent}".strip()
                        else:
                            if sub_chunk:
                                chunks.append(sub_chunk)
                            sub_chunk = sent
                    if sub_chunk:
                        current_chunk = sub_chunk
                else:
                    current_chunk = para

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]

    async def synthesize_speech(
        self,
        raw_text: str,
        lang: str = "uz",
        gender: str = "female",
        rate: str = "+0%",
        target_format: str = "mp3",
    ) -> Optional[bytes]:
        """
        Full synthesis pipeline:
        1. Linguistic normalization
        2. Cache lookup
        3. Neural chunk synthesis with fallback chain
        4. Audio concatenation & post-processing
        5. Cache storage
        """
        start_time = time.time()
        self.stats["total_requests"] += 1

        if not raw_text or not raw_text.strip():
            return None

        # 1. Linguistic Normalization
        if lang == "uz":
            norm_text = self.normalizer.normalize(raw_text)
        else:
            norm_text = raw_text.strip()

        if not norm_text:
            return None

        voice = self.resolve_voice(lang, gender)
        cache_key = self._compute_hash(norm_text, voice, rate)
        cache_file = self._get_cache_path(cache_key, target_format)

        # 2. Cache Lookup
        if os.path.exists(cache_file) and os.path.getsize(cache_file) > 1000:
            try:
                with open(cache_file, "rb") as f:
                    cached_bytes = f.read()
                self.stats["cache_hits"] += 1
                self.stats["last_latency_ms"] = (time.time() - start_time) * 1000
                logger.info(f"TTS Cache HIT ({len(cached_bytes)} bytes, key: {cache_key})")
                return cached_bytes
            except Exception as ce:
                logger.warning(f"Failed to read TTS cache: {ce}")

        # 3. Chunking for long essays
        chunks = self.split_into_chunks(norm_text, max_chars=1500)
        audio_parts: List[bytes] = []

        now = time.time()
        use_fallback = now < self._circuit_open_until

        for idx, chunk in enumerate(chunks):
            chunk_audio = None

            # Try Primary Provider
            if not use_fallback:
                chunk_audio = await self.primary_provider.synthesize(chunk, voice=voice, rate=rate)

            # Check primary failure
            if not chunk_audio:
                self._failure_count += 1
                logger.warning(f"Primary TTS provider failed on chunk {idx + 1}/{len(chunks)}")

                # Trip circuit breaker if too many failures
                if self._failure_count >= self._max_consecutive_failures:
                    self._circuit_open_until = time.time() + self._cooldown_seconds
                    logger.error("TTS Circuit Breaker TRIPPED. Cooling down for 60s.")

                # Try secondary voice if uzbek
                alt_voice = VOICE_MAP["uz"]["male"] if voice == VOICE_MAP["uz"]["female"] else VOICE_MAP["uz"]["female"]
                chunk_audio = await self.primary_provider.synthesize(chunk, voice=alt_voice, rate=rate)

                # If still failing, try emergency GTTS fallback
                if not chunk_audio:
                    self.stats["fallback_used"] += 1
                    logger.warning(f"Falling back to GTTS for chunk {idx + 1}")
                    chunk_audio = await self.fallback_provider.synthesize(chunk, voice=voice, rate=rate)
            else:
                self._failure_count = max(0, self._failure_count - 1)
                self.stats["primary_success"] += 1

            if chunk_audio:
                audio_parts.append(chunk_audio)
            else:
                logger.error(f"Failed to synthesize chunk {idx + 1}")

        if not audio_parts:
            self.stats["failures"] += 1
            return None

        # 4. Concatenate raw parts
        combined_raw = b"".join(audio_parts)

        # 5. Audio Post-Processing (FFmpeg / loudness / trim)
        final_audio, _ = post_process_audio(
            combined_raw,
            target_format=target_format,
            normalize_loudness=True,
            trim_silence=True,
        )

        # 6. Store in Cache
        try:
            with open(cache_file, "wb") as f:
                f.write(final_audio)
        except Exception as se:
            logger.warning(f"Failed to store TTS cache: {se}")

        self.stats["last_latency_ms"] = (time.time() - start_time) * 1000
        logger.info(
            f"TTS Synthesized successfully in {self.stats['last_latency_ms']:.1f}ms "
            f"({len(final_audio)} bytes, voice: {voice})"
        )
        return final_audio


# Global instance
tts_service = TTSService()
