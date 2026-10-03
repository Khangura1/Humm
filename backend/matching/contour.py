import numpy as np

from matching.config import FloatArray

# using the note A4 as reference point/standard tune
A4_HZ: float = 440.0
A4_MIDI: float = 69.0
SEMITONES_PER_OCTAVE: float = 12.0


def hz_to_midi(f0_hz: FloatArray) -> FloatArray:
    """Input: frequency in Hz, Output: Corresponding MIDI note number"""
    return A4_MIDI + (
        SEMITONES_PER_OCTAVE * np.log2(f0_hz / A4_HZ)
    )  # formula to convert hz to midi note number
