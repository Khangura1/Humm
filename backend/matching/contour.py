"""Turns Pitches into the shape of a melody that ignores key"""

import numpy as np

from matching.config import FloatArray, MatchConfig
from matching.errors import NotEnoughAudioError


# using the note A4 as reference point/standard tune
A4_HZ: float = 440.0
A4_MIDI: float = 69.0
SEMITONES_PER_OCTAVE: float = 12.0


def hz_to_midi(f0_hz: FloatArray) -> FloatArray:
    """Input: frequency in Hz, Output: Corresponding MIDI note number"""
    return A4_MIDI + (
        SEMITONES_PER_OCTAVE * np.log2(f0_hz / A4_HZ)
    )  # formula to convert hz to midi note number


def median_filter(x: FloatArray, width: int) -> FloatArray:
    """Replaces each value with middle value of itself with neighbors"""
    if len(x) == 0:
        return x.copy()
    half = width // 2
    padded = np.pad(x, half, mode="edge")
    result = np.zeros(len(x))
    for i in range(len(x)):
        window = padded[i : i + width]
        result[i] = np.median(window)
    return result


def normalize_contour(semitones: FloatArray, config: MatchConfig) -> FloatArray:
    """Takes pitch sequenc from songs or humms, remove its key, produce smoothed shape"""

    has_pitch = ~np.isnan(semitones)
    pitched = semitones[has_pitch]
    if len(pitched) == 0:
        raise NotEnoughAudioError("No pitch in recording")

    centered = pitched - np.median(pitched)  # removes key
    smoothed = median_filter(centered, config.median_width)  # smooths out audio
    clipped = np.clip(smoothed, -config.clip_semitones, config.clip_semitones)
    # removes when more than one octave from the middle
    shortened = clipped[:: config.downsample]

    if len(shortened) < config.min_contour_length:
        raise NotEnoughAudioError("Hum is too short. Hum for longer")
    return shortened
