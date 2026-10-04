"""reading reference melodies from MIDI files"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pretty_midi

from matching.config import FloatArray


@dataclass(frozen=True)
class Note:
    """single note for melody"""

    midi: int
    start_s: float
    end_s: float


def start_time(note: Note) -> float:
    """what notes are sorted by at start"""
    return note.start_s


def read_midi_notes(path: Path) -> list[Note]:
    midi_file = pretty_midi.PrettyMIDI(str(path))
    notes = []
    for instrument in midi_file.instruments:
        if instrument.is_drum:
            continue
        for midi_note in instrument.notes:
            note = Note(
                midi=midi_note.pitch, start_s=midi_note.start, end_s=midi_note.end
            )
            notes.append(note)
    notes.sort(key=start_time)
    return notes


def notes_to_frames(notes: list[Note], hop_seconds: float) -> FloatArray:
    """Turn notes into a single MIDI number per frame"""
    if len(notes) == 0:
        return np.zeros(0)
    last_end_s = 0.0
    for note in notes:
        last_end_s = max(last_end_s, note.end_s)
    frame_count = round(last_end_s / hop_seconds)
    frames = np.full(frame_count, np.nan)

    for note in notes:
        start_frame = round(note.start_s / hop_seconds)
        end_frame = min(round(note.end_s / hop_seconds), frame_count)
        for i in range(start_frame, end_frame):
            if np.isnan(frames[i]) or note.midi > frames[i]:
                frames[i] = note.midi

    return frames
