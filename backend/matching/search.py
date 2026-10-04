"""Song Ranking System"""

from dataclasses import dataclass

import numpy as np

from matching.config import FloatArray, MatchConfig
from matching.dtw import subsequence_dtw
from matching.index import MelodyIndex


@dataclass(frozen=True)
class Match:
    """Class for possible matches"""

    song_id: str
    difference: float  # avg gap in semitones
    similarity_score: float  # 0.0 to 1.0 scale


def rank_songs(hum: FloatArray, index: MelodyIndex, config: MatchConfig) -> list[Match]:
    """Compare hums with catalog and return list in order of best matches"""
    song_differences = []
    for song_id, song_contour in index.contours.items():
        lowest_difference = find_lowest_difference(hum, song_contour, config)
        if not np.isinf(lowest_difference):
            song_differences.append((lowest_difference, song_id))
    song_differences.sort()

    matches = []
    for lowest_difference, song_id in song_differences[: config.match_count]:
        matches.append(
            Match(
                song_id=song_id,
                difference=lowest_difference,
                similarity_score=score(lowest_difference),
            )
        )
    return matches


def find_lowest_difference(
    hum: FloatArray, song_contour: FloatArray, config: MatchConfig
) -> float:
    """tries hum shifted up or down, keeps lowest difference"""
    lowest_difference = np.inf
    for shift in config.semitone_shifts:
        result = subsequence_dtw(hum + shift, song_contour)
        lowest_difference = min(lowest_difference, result.difference)
    return lowest_difference


def score(difference: float) -> float:
    """turns the difference into a score from 0 to 1"""
    return 1.0 / (1.0 + difference)
