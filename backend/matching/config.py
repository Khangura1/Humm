"""shared type for audio matching"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class PitchConfig:
    """values for pitch detection/matching with YIN method"""

    sample_rate_hz: int = 16000  # excpected samples per second
    window_size: int = 1024  # amount of samples in each window
    hop_size: int = 160  # samples to move forward for each window
    fmin_hz: float = 80.0  # minimum frequency to detect
    fmax_hz: float = 800.0  # maximum frequency to detect
    yin_thresh: float = 0.1  # threshold for YIN algorithm
    min_rms_db: float = -40.0  # minimumn decibal level (relative to loudest frame )for a pitch to be considered valid
    min_run_ms: float = 50.0  # minimum duration for a pitch to be considered valid


@dataclass(frozen=True)
class PreprocessConfig:
    """values for preproccessing audio before pitch detection"""

    cutoff_hz: float = 70.0  # cutoff frequency for high-pass filter
    target_peak: float = 0.9  # scales audio towards 90% of max volume
    bottom_thresh_db: float = (
        -35.0
    )  # frames with RMS below this threshold will be considered silent
    surrounding_audio_ms: float = (
        50.0  # amount of audio to include before and after based on loudness
    )
