"""Pitch Tracking with YIN algorithm"""

from dataclasses import dataclass

import numpy as np

from matching.config import BoolArray, FloatArray, PitchConfig


@dataclass(frozen=True)
class PitchTrack:
    """Pitch of single recording, tracked through 4 arrays"""

    times_s: FloatArray  # second each frame starts
    f0_hz: FloatArray  # pitch of each frame
    clarity: FloatArray  # clarity/clearness of pitch
    rms: FloatArray  # pitch loudness


def give_rms(frame: FloatArray) -> float:
    """Avg loudness of a frame"""
    return float(np.sqrt(np.mean(frame * frame)))


def give_diff(frame: FloatArray, max_lag: int) -> FloatArray:
    """YIN step 2: gives difference between the frame and itself at different shifts"""
    window = len(frame) - max_lag
    diff = np.zeros(max_lag + 1)

    for lag in range(max_lag + 1):
        original = frame[0:window]
        shifted = frame[lag : lag + window]
        gap = original - shifted
        diff[lag] = np.sum(gap * gap)

    return diff


def give_cmnd(diff: FloatArray) -> FloatArray:
    """YIN step 3: each value divded by average of all values before it.
    cmnd -> cumulative mean normalized difference"""

    cmnd = np.ones(len(diff))
    diff_sum = 0.0

    for lag in range(1, len(diff)):
        diff_sum += diff[lag]
        if diff_sum == 0.0:
            cmnd[lag] = 1.0
        else:
            average = diff_sum / lag
            cmnd[lag] = diff[lag] / average

    return cmnd


def give_absolute_thresh(cmnd: FloatArray, thresh: float, min_lag: int) -> int | None:
    """Yin step 4: first dip below threshold, returns none if no threshhold"""
    lag = min_lag
    while lag < len(cmnd):
        if cmnd[lag] < thresh:
            while lag + 1 < len(cmnd) and cmnd[lag + 1] < cmnd[lag]:
                lag += 1
            return lag
        lag += 1
    return None


def parabolic_interpolation(values: FloatArray, i: int) -> float:
    """Yin step 5: find the bottom of a dip between two samples"""
    if i <= 0 or i >= len(values) - 1:
        return float(i)

    a = values[i - 1]
    b = values[i]
    c = values[i + 1]

    bottom = a - (2 * b) + c

    if bottom == 0:
        return float(i)

    return float(i + (a - c) / (2 * bottom))


def remove_short(voiced: BoolArray, min_frames: int) -> BoolArray:
    """silence voiced stretches shorter than minimum frame"""
    cleaned = voiced.copy()
    run_start = None
    for i in range(len(cleaned) + 1):
        is_voiced = i < len(cleaned) and cleaned[i]
        if is_voiced and run_start is None:
            run_start = i
        elif not is_voiced and run_start is not None:
            if i - run_start < min_frames:
                for j in range(run_start, i):
                    cleaned[j] = False
            run_start = None
    return cleaned


def track_pitch(signal: FloatArray, config: PitchConfig) -> PitchTrack:
    """Measures pitch throughout a recording"""

    max_lag = int(config.sample_rate_hz / config.fmin_hz)
    min_lag = int(config.sample_rate_hz / config.fmax_hz)

    if len(signal) < config.window_size:
        empty = np.zeros(0)
        return PitchTrack(empty, empty, empty, empty)

    frame_count = 1 + (len(signal) - config.window_size) // config.hop_size
    times_s = np.zeros(frame_count)
    f0_hz = np.full(frame_count, np.nan)
    clarity = np.ones(frame_count)
    rms = np.zeros(frame_count)

    for i in range(frame_count):
        start = i * config.hop_size
        frame = signal[start : start + config.window_size]

        times_s[i] = start / config.sample_rate_hz
        rms[i] = give_rms(frame)
        diff = give_diff(frame, max_lag)
        cmnd = give_cmnd(diff)
        best_lag = give_absolute_thresh(cmnd, config.yin_thresh, min_lag)
        if best_lag is None:
            continue
        exact_lag = parabolic_interpolation(cmnd, best_lag)
        f0_hz[i] = config.sample_rate_hz / exact_lag
        clarity[i] = cmnd[best_lag]

    return PitchTrack(times_s, f0_hz, clarity, rms)


def voicing_mask(track: PitchTrack, config: PitchConfig) -> BoolArray:
    """marks the frames that contain real humming"""
    frame_count = len(track.f0_hz)
    voiced = np.zeros(frame_count, dtype=bool)

    if frame_count == 0:
        return voiced  # no frames in recording

    loudest = np.max(track.rms)
    if loudest == 0:
        return voiced  # silent recording

    for i in range(frame_count):
        has_pitch = not np.isnan(track.f0_hz[i])

        loudness_db = 20 * np.log10(track.rms[i] / loudest)
        is_loud = loudness_db >= config.min_rms_db
        if has_pitch and is_loud:
            voiced[i] = True
    min_frames = round((config.min_run_ms / 1000) / config.hop_time_s)
    return remove_short(voiced, min_frames)
