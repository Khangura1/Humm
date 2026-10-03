"""reading reference melodies from MIDI files"""
from dataclasses import dataclass
from pathlib import Path


import numpy as np
import pretty_midi

@dataclass(frozen=True)
class Note:
    """single note for melody"""

    midi: int
    start_s: float
    end_s: float

def read_midi_note(path: Path) -> list[Note]:
    midi_file = pretty_midi.PrettyMIDI(str(path))
    notes = [] 
    for instrument.is_drum:
        continue


