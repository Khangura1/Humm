"""Song Ranking System"""

from dataclasses import dataclass

import numpy as np

from matching.config import MatchConfig, FloatArray
from matching.dtw import subsequence_dtw
from matching.index import MelodyIndex


@dataclass(frozen=True)
class Match:
    """Class for possible matches"""

    song_id: str
    difference: float  # avg gap in semitones
    similarity_score: float  # 0.0 to 1.0 scale


def rank_songs(hum: FloatArray, song: MelodyIndex, config: MatchConfig) -> list[Match]:
    """Compare hums with catalog and return list in order of best matches"""
    song_differences = []
    for song_id, song_contour in song.contours.items():
        difference = lowest_difference(hum, song_contour, config)
        if not np.isinf(best_cost):
            song_differences.append((difference, song_id))
    song_differences.sort()

    matches = []
    for difference, song_id in song_differences[: config.match_count]:
        matches.append(
            Match(
                song_id=song_id,
                difference=difference,
                similarity_score=score(difference),
            )
        )
    return matches
