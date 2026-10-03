"""Write catalog songs as MIDI files

Run from backend/: python -m scripts.make_midi"""

from pathlib import Path
import pretty_midi

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "midi" / "custom"
SPB = 0.5  # Seconds per beat
NOTE_LENGTH = 0.9  # notes play for 90% of normal time, repeats are seperate

NOTE_NUMBERS = {
    "C2": 36,
    "D2": 38,
    "E2": 40,
    "F2": 41,
    "G2": 43,
    "A2": 45,
    "B2": 47,
    "C3": 48,
    "D3": 50,
    "E3": 52,
    "F3": 53,
    "G3": 55,
    "A3": 57,
    "B3": 59,
    "C4": 60,
    "D4": 62,
    "E4": 64,
    "F4": 65,
    "G4": 67,
    "A4": 69,
    "B4": 71,
    "C5": 72,
    "D5": 74,
    "E5": 76,
    "F5": 77,
    "G5": 79,
    "A5": 81,
    "B5": 83,
    "C6": 84,
    "D6": 86,
    "E6": 88,
    "F6": 89,
    "G6": 91,
    "A6": 93,
    "B6": 95,
}

SONGS = {
    "ode_to_joy": """
        E4 E4 F4 G4  G4 F4 E4 D4  C4 C4 D4 E4  E4:1.5 D4:0.5 D4:2
        E4 E4 F4 G4  G4 F4 E4 D4  C4 C4 D4 E4  D4:1.5 C4:0.5 C4:2
    """,
    "twinkle": """
        C4 C4 G4 G4  A4 A4 G4:2  F4 F4 E4 E4  D4 D4 C4:2
        G4 G4 F4 F4  E4 E4 D4:2  G4 G4 F4 F4  E4 E4 D4:2
        C4 C4 G4 G4  A4 A4 G4:2  F4 F4 E4 E4  D4 D4 C4:2
    """,
    "jingle_bells": """
        E4 E4 E4:2  E4 E4 E4:2  E4 G4 C4:1.5 D4:0.5  E4:4
        F4 F4 F4:1.5 F4:0.5  F4 E4 E4 E4:0.5 E4:0.5  E4 D4 D4 E4  D4:2 G4:2
        E4 E4 E4:2  E4 E4 E4:2  E4 G4 C4:1.5 D4:0.5  E4:4
        F4 F4 F4 F4  F4 E4 E4 E4:0.5 E4:0.5  G4 G4 F4 D4  C4:4
    """,
    "amazing_grace": """
        G3  C4:2 E4:0.5 C4:0.5  E4:2 D4  C4:2 A3  G3:2 G3
        C4:2 E4:0.5 C4:0.5  E4:2 D4  G4:3  G4:2 E4
        G4:2 E4:0.5 C4:0.5  E4:2 D4  C4:2 A3  G3:2 G3
        C4:2 E4:0.5 C4:0.5  E4:2 D4  C4:3
    """,
    "happy_birthday": """
        G4:0.75 G4:0.25  A4 G4 C5  B4:2 G4:0.75 G4:0.25
        A4 G4 D5  C5:2 G4:0.75 G4:0.25
        G5 E5 C5  B4 A4 F5:0.75 F5:0.25  E5 C5 D5  C5:3
    """,
}


def write_song(name: str, melody: str) -> None:
    """Turn one melody string into a MIDI file named after the song."""
    midi_file = pretty_midi.PrettyMIDI()
    flute = pretty_midi.Instrument(program=73)  # 73 is flute in General MIDI

    time_s = 0.0
    for token in melody.split():
        if ":" in token:
            note_name, beats_text = token.split(":")
            beats = float(beats_text)
        else:
            note_name = token
            beats = 1.0
        length_s = beats * SPB
        note = pretty_midi.Note(
            velocity=100,
            pitch=NOTE_NUMBERS[note_name],
            start=time_s,
            end=time_s + length_s * NOTE_LENGTH,
        )
        flute.notes.append(note)
        time_s += length_s

    midi_file.instruments.append(flute)
    midi_file.write(str(OUTPUT_DIR / f"{name}.mid"))
    print(f"{name}.mid: {len(flute.notes)} notes, {time_s:.1f} s")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, melody in SONGS.items():
        write_song(name, melody)


if __name__ == "__main__":
    main()
