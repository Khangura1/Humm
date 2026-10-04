"""Shape of currently cataloged songs"""

from pathlib import Path

import numpy as np

from matching.catalog import CatalogEntry
from matching.config import FloatArray, MatchConfig, PitchConfig
from matching.contour import normalize_contour
from matching.melody import notes_to_frames, read_midi_notes


class MelodyIndex:
    """Connects song ID to the songs shape"""

    def __init__(self, contours: dict[str, FloatArray]) -> None:
        self.contours = contours

    @classmethod
    def build(
        cls,
        entries: list[CatalogEntry],
        pitch_config: PitchConfig,
        match_config: MatchConfig,
    ) -> "MelodyIndex":
        """Every catalog song split up into MIDI, notes, frames, shape"""
        contours = {}
        for entry in entries:
            notes = read_midi_notes(entry.midi_path)
            frames = notes_to_frames(notes, pitch_config.hop_time_s)
            contours[entry.song_id] = normalize_contour(frames, match_config)
        return cls(contours)

    def save(self, path: Path) -> None:
        """Saves every shape into one .npz file"""
        np.savez(path, **self.contours)  # type: ignore[arg-type]

    @classmethod
    def load(cls, path: Path) -> "MelodyIndex":
        """Reads shapes back from a saved file"""
        contours = {}
        with np.load(path) as saved:
            for song_id in saved.files:
                contour = saved[song_id]
                contour.flags.writeable = False  # nothing may change it later
                contours[song_id] = contour
        return cls(contours)
