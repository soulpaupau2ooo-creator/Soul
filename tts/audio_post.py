"""
Audio Post-Processing Module for Soulbekbot TTS.

Provides:
- Silence trimming
- EBU R128 loudness normalization
- Optional Telegram OPUS encoding
- Graceful no-op fallback when FFmpeg is not installed
"""

import io
import logging
import os
import shutil
import subprocess
import tempfile
from typing import Optional, Tuple

logger = logging.getLogger("TTSAudioPost")

FFMPEG_PATH: Optional[str] = shutil.which("ffmpeg")
FFPROBE_PATH: Optional[str] = shutil.which("ffprobe")


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg executable is discovered on system PATH."""
    return FFMPEG_PATH is not None


def post_process_audio(
    audio_bytes: bytes,
    target_format: str = "mp3",
    normalize_loudness: bool = True,
    trim_silence: bool = True,
) -> Tuple[bytes, str]:
    """
    Apply professional audio post-processing to raw TTS audio bytes.

    Args:
        audio_bytes: Raw audio byte content (usually MP3).
        target_format: 'mp3' or 'ogg'.
        normalize_loudness: Apply EBU R128 speech normalization.
        trim_silence: Trim leading and trailing dead air.

    Returns:
        Tuple of (processed_bytes, mime_type).
    """
    if not audio_bytes:
        return b"", "audio/mpeg"

    if not is_ffmpeg_available():
        logger.debug("FFmpeg not installed, returning unmodified TTS audio stream.")
        mime = "audio/ogg" if target_format == "ogg" else "audio/mpeg"
        return audio_bytes, mime

    temp_in = None
    temp_out = None
    try:
        # Create temp files
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f_in:
            f_in.write(audio_bytes)
            temp_in = f_in.name

        out_suffix = f".{target_format}"
        temp_out = temp_in + f"_processed{out_suffix}"

        # Construct ffmpeg filter chain
        filters = []
        if trim_silence:
            # Leave ~80ms headroom
            filters.append("silenceremove=start_periods=1:start_duration=0.08:start_threshold=-50dB:detection=peak")

        if normalize_loudness:
            # EBU R128 for speech: I=-16 LUFS, LRA=11, TP=-1.5 dBTP
            filters.append("loudnorm=I=-16:LRA=11:TP=-1.5")

        filter_arg = ",".join(filters) if filters else None

        cmd = [FFMPEG_PATH, "-y", "-i", temp_in]
        if filter_arg:
            cmd.extend(["-af", filter_arg])

        if target_format == "ogg":
            cmd.extend([
                "-c:a", "libopus",
                "-b:a", "48k",
                "-ar", "48000",
                "-ac", "1",
                "-application", "voip"
            ])
            mime = "audio/ogg"
        else:
            cmd.extend([
                "-c:a", "libmp3lame",
                "-b:a", "64k",
                "-ar", "24000",
                "-ac", "1"
            ])
            mime = "audio/mpeg"

        cmd.append(temp_out)

        # Run process safely
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15.0,
            check=False
        )

        if res.returncode == 0 and os.path.exists(temp_out) and os.path.getsize(temp_out) > 0:
            with open(temp_out, "rb") as f_out:
                processed_bytes = f_out.read()
            return processed_bytes, mime
        else:
            err_msg = res.stderr.decode("utf-8", errors="ignore")[:200]
            logger.warning(f"FFmpeg processing failed (code {res.returncode}): {err_msg}. Using fallback audio.")
            return audio_bytes, "audio/mpeg"

    except Exception as e:
        logger.error(f"Error during audio post-processing: {e}")
        return audio_bytes, "audio/mpeg"

    finally:
        # Cleanup temp files reliably
        if temp_in and os.path.exists(temp_in):
            try:
                os.remove(temp_in)
            except Exception:
                pass
        if temp_out and os.path.exists(temp_out):
            try:
                os.remove(temp_out)
            except Exception:
                pass
