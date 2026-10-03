import struct
from pathlib import Path
from typing import BinaryIO

import numpy as np

from matching.config import FloatArray

PCM_FORMAT = 1
MONO = 1
RIFF_HEADER_SIZE = 12
CHUNK_HEADER_SIZE = 8
FMT_CHUNK_SIZE = 16
INT16_SCALE = 32768.0
INT16_MAX = 32767.0

SILENCE = 128.0


def wav_chunk(f: BinaryIO) -> dict[bytes, bytes]:
    """read every chunk following RIFF header and returns a name + content map"""
    chunks: dict[bytes, bytes] = {}
    while True:
        header = f.read(CHUNK_HEADER_SIZE)
        if len(header) == 0:
            break
        name = header[0:4]
        size = int(struct.unpack("<I", header[4:8])[0])
        content = f.read(size)

        if size % 2 == 1:
            f.read(1)  # skip padding byte

        chunks[name] = content
    return chunks


def parse(fmt_content: bytes) -> tuple[int, int, int, int]:
    """Parses content then returns: sample rate, channels, bits per sample, and format"""

    audio_format = int(struct.unpack("<H", fmt_content[0:2])[0])
    channels = int(struct.unpack("<H", fmt_content[2:4])[0])
    sample_rate = int(struct.unpack("<I", fmt_content[4:8])[0])
    bits_per_sample = int(struct.unpack("<H", fmt_content[14:16])[0])

    return sample_rate, channels, bits_per_sample, audio_format


def decode_samples(data: bytes, channels: int, bits_per_sample: int) -> FloatArray:
    """Turns raw audio into mono decimals between -1.0 and 1.0"""
    if bits_per_sample == 16:
        whole_numbers = np.frombuffer(data, dtype="<i2")
        samples = whole_numbers.astype(np.float64) / INT16_SCALE
    elif bits_per_sample == 8:
        whole_numbers = np.frombuffer(data, dtype="<u1")
        samples = (whole_numbers.astype(np.float64) - SILENCE) / SILENCE

    if channels == 1:
        mono = samples
    else:
        total = np.zeros(len(samples) // channels)
    for channel in range(channels):
        total += samples[channel::channels]
    mono = total / channels

    result: FloatArray = mono.astype(np.float64)
    return result


def read_wav(path: Path) -> tuple[FloatArray, int]:
    """reads WAV file and returns monosamples between -1 and 1 + sample rate"""
    with open(path, "rb") as f:
        riff_header = f.read(RIFF_HEADER_SIZE)
        chunks = wav_chunk(f)
    audio_format, channels, sample_rate_hz, bits_per_sample = parse(chunks[b"fmt "])
    samples = decode_samples(chunks[b"data"], channels, bits_per_sample)

    return samples, sample_rate_hz


def write_wav(path: Path, signal: FloatArray, sample_rate_hz: int) -> None:
    """Write samples between -1.0 and 1.0 as a WAV file"""
    clipped = np.clip(signal, -1.0, 1.0)

    whole_numbers = (clipped * INT16_SCALE).astype("<i2")
    data = whole_numbers.tobytes()

    bytes_per_second = sample_rate_hz * 16 * PCM_FORMAT
    bytes_per_frame = 2 * PCM_FORMAT

    fmt_content = struct.pack(
        "<HHIIHH",
        PCM_FORMAT,
        MONO,
        sample_rate_hz,
        bytes_per_second,
        bytes_per_frame,
        16,
    )
    fmt_chunk = b"fmt " + struct.pack("<I", FMT_CHUNK_SIZE) + fmt_content
    data_chunk = b"data" + struct.pack("<I", len(data)) + data
    riff_size = 4 + len(fmt_chunk) + len(data_chunk)
    riff_header = b"RIFF" + struct.pack("<I", riff_size) + b"WAVE"

    with open(path, "wb") as f:
        f.write(riff_header)
        f.write(fmt_chunk)
        f.write(data_chunk)
