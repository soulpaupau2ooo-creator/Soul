"""
TTS Module for Soulbekbot.
"""

from tts.service import TTSService, tts_service, VOICE_MAP
from tts.uzbek_normalizer import UzbekTextNormalizer
from tts.audio_post import post_process_audio, is_ffmpeg_available

__all__ = [
    "TTSService",
    "tts_service",
    "VOICE_MAP",
    "UzbekTextNormalizer",
    "post_process_audio",
    "is_ffmpeg_available",
]
