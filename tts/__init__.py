"""
TTS Module for Soulbekbot.
"""

try:
    from tts.service import TTSService, tts_service, VOICE_MAP
except ImportError:  # pragma: no cover - optional/runtime-only TTS dependencies
    TTSService = None  # type: ignore[misc,assignment]
    tts_service = None  # type: ignore[assignment]
    VOICE_MAP = {}

from tts.uzbek_normalizer import UzbekTextNormalizer
try:
    from tts.audio_post import post_process_audio, is_ffmpeg_available
except ImportError:  # pragma: no cover - optional post-processing dependency
    post_process_audio = None  # type: ignore[assignment]
    is_ffmpeg_available = lambda: False  # type: ignore[assignment]

__all__ = [
    "TTSService",
    "tts_service",
    "VOICE_MAP",
    "UzbekTextNormalizer",
    "post_process_audio",
    "is_ffmpeg_available",
]
