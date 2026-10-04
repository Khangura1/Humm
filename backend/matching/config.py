"""shared type for audio matching"""

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

type FloatArray = NDArray[np.float64]
type BoolArray = NDArray[np.bool_]


@dataclass(frozen=True)
class PitchConfig:
    """values for pitch detection/matching with YIN method"""

    sample_rate_hz: int = 16000  # excpected samples per second
    window_size: int = 1024  # amount of samples in each window
    hop_size: int = 160  # samples to move forward for each window
    fmin_hz: float = 80.0  # minimum frequency to detect
    fmax_hz: float = 800.0  # maximum frequency to detect
    yin_thresh: float = 0.1  # threshold for YIN algorithm
    min_rms_db: float = -40.0  # minimum decibel level (relative to loudest frame )
    min_run_ms: float = 50.0  # minimum duration for a pitch to be considered valid

    @property
    def hop_time_s(self) -> float:
        """time between frames/durating of hop"""
        return self.hop_size / self.sample_rate_hz


@dataclass(frozen=True)
class MatchConfig:
    """Values for turning pitches into shapes and matching"""

    median_width: int = 5  # looks at middle values + 2 surrounding
    clip_semitones: float = 12.0  # jumps larger than one octave would be an error
    downsample: int = 5  # reduces amount of values considered to 1 / 5
    min_contour_length: int = 10  # values fewer than 10 cant be matched
    semitone_shifts: tuple[int, ...] = (-1, 0, 1)
    match_count: int = 1  # number of top matches given


@dataclass(frozen=True)
class AudioEngineConfig:
    """All audio engines"""

    pitch: PitchConfig = field(default_factory=PitchConfig)
    match: MatchConfig = field(default_factory=MatchConfig)
    min_duration_s: float = 1.0  # shortest hum allowed is 1 second
    min_voiced_ratio: float = 0.2  # 1 / 5 of clip must be voiced humming
