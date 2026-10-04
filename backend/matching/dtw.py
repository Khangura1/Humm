"""subsequence dynamic time warping algorithm == lining up a hum with a song"""

from dataclasses import dataclass

from matching.config import FloatArray

import numpy as np


@dataclass(frozen=True)
class DTWResult:
    """Score for song similarity + location of similarity"""

    difference: float  # average difference between each hum value
    end_index: int  # position in song where best match ends


def difference_matrix(hum: FloatArray, song: FloatArray) -> FloatArray:
    """difference between every hum value and every song value"""
    return np.abs(hum[:, None] - song[None, :])


def accumulate(difference: FloatArray) -> FloatArray:
    """Fills the DTW table with smallest difference"""
    n_rows, n_cols = difference.shape
    total = np.full((n_rows, n_cols), np.inf)

    for col in range(n_cols):
        total[0, col] = difference[0, col]

    # Hum arrives at a cell by being 1:1 (same speed), 1:2 (.5x), or 2:1 (2x)
    # To be matched, Hum can be at most twice as fast or twice as slow

    for row in range(1, n_rows):
        for col in range(1, n_cols):
            best_move = total[row - 1, col - 1]
            if row >= 2 and total[row - 2, col - 1] < best_move:
                best_move = total[row - 2, col - 1]
            if col >= 2 and total[row - 1, col - 2] < best_move:
                best_move = total[row - 1, col - 2]
            total[row, col] = difference[row, col] + best_move

    return total


def subsequence_dtw(humm: FloatArray, song: FloatArray) -> DTWResult:
    """finds stretch of song that best matches humm"""
    if len(humm) == 0 or len(song) == 0:
        return DTWResult(difference=np.inf, end_index=-1)
    total = accumulate(difference_matrix(humm, song))
    last_row = total[-1]
    end_index = int(np.argmin(last_row))
    best_total = last_row[end_index]
    if np.isinf(best_total):  # song too short for hum
        return DTWResult(difference=np.inf, end_index=-1)
    return DTWResult(difference=float(best_total / len(humm)), end_index=end_index)
