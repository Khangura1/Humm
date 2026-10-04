"""Complete recognition system"""

from dataclasses import dataclass

import numpy as np

from matching.config import AudioEngineConfig, BoolArray, FloatArray
from matching.contour import hz_to_midi, normalize_contour
from matching.errors import NotEnoughAudioError
from matching.index import MelodyIndex
from matching.pitch import track_pitch, voicing_mask
from matching.search import Match, rank_songs


@dataclass(frozen=True)
class Analysis:
    """everything the system learns from one user hum"""

    duration_s: float
    voiced_ratio: float  # fraction of frames with audible humming
    contour: FloatArray  # normalized shape of hum
    matches: list[Match]


def check_duration(duration_s: float, config: AudioEngineConfig) -> None:
    if duration_s < config.min_duration_s:
        raise NotEnoughAudioError(
            f"The recording is {duration_s:.1f} s long."
            f" Hum for at least {config.min_duration_s:.0f} s."
        )


def check_voiced_ratio(voiced_ratio: float, config: AudioEngineConfig) -> None:
    if voiced_ratio < config.min_voiced_ratio:
        raise NotEnoughAudioError("Try humming louder or closer")


def voiced_pitches(f0_hz: FloatArray, voiced: FloatArray) -> BoolArray:
    """A copy of pitches with every unvoiced frame set to NaN"""
    pitches = f0_hz.copy()
    for i in range(len(pitches)):
        if not voiced[i]:
            pitches[i] = np.nan
    return pitches


def analyze(
    signal: FloatArray,
    sample_rate_hz: int,
    index: MelodyIndex,
    config: AudioEngineConfig,
) -> Analysis:
    """Recognize the hum and return the top matches"""

    duration_s = len(signal) / sample_rate_hz
    check_duration(
        duration_s, config
    )  # Rejects clips that are too short before anything else

    track = track_pitch(signal, config.pitch)
    voiced = voicing_mask(track, config.pitch)
    voiced_ratio = float(np.mean(voiced))
    check_voiced_ratio(
        voiced_ratio, config
    )  # goes through audio recording and determines which sections contain humming

    semitones = hz_to_midi(
        voiced_pitches(track.f0_hz, voiced)
    )  # unvoiced frames become NaN, then Hz are converted into Midi
    contour = normalize_contour(semitones, config.match)
    matches = rank_songs(contour, index, config.match)  # ranks against every song

    return Analysis(duration_s, voiced_ratio, contour, matches)
