"""checking an upload recording and turning it into samples"""

import logging
import subprocess
import tempfile

from fastapi import HTTPException

from matching.config import FloatArray
from matching.errors import WavFormatError
from matching.wav import read_wav_bytes

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {  # Browser recording types
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
}


def check_upload(content_type: str | None, size_bytes: int, max_bytes: int) -> None:
    """Stop the request if audio incompatible"""
    base_type = (content_type or "").split(";")[0].strip().lower()
    if base_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415, detail="That isn't a supported audio type."
        )
    if size_bytes > max_bytes:
        raise HTTPException(status_code=413, detail="That recording is too large.")


def decode_audio(data: bytes, sample_rate_hz: int, timeout_s: float) -> FloatArray:
    """Convert recording into mono samples"""
    with tempfile.NamedTemporaryFile(suffix=".upload") as upload_file:
        upload_file.write(data)
        upload_file.flush()
        wav_bytes = run_ffmpeg(upload_file.name, sample_rate_hz, timeout_s)

    try:
        signal, _ = read_wav_bytes(wav_bytes)
    except WavFormatError as error:
        logger.warning("Couldn't read ffmpeg's WAV output: %s", error)
        raise HTTPException(
            status_code=422, detail="That recording couldn't be read."
        ) from error
    return signal


def run_ffmpeg(input_path: str, sample_rate_hz: int, timeout_s: float) -> bytes:
    """Have ffmpeg turn the file into 16-bit mono WAV"""
    command = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-i",
        input_path,
        "-map_metadata",
        "-1",
        "-fflags",
        "+bitexact",
        "-f",
        "wav",
        "-ac",
        "1",
        "-ar",
        str(sample_rate_hz),
        "-acodec",
        "pcm_s16le",
        "pipe:1",
    ]
    try:
        result = subprocess.run(
            command, capture_output=True, timeout=timeout_s, check=False
        )
    except subprocess.TimeoutExpired as error:
        raise HTTPException(
            status_code=422, detail="That recording took too long."
        ) from error

    return result.stdout
