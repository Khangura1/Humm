"""Song catalog for app"""

import json
from dataclasses import dataclass
from pathlib import Path

from matching.errors import CatalogError


@dataclass(frozen=True)
class CatalogEntry:
    """Information for a single song"""

    song_id: str
    title: str
    artist: str
    source: str
    midi_path: Path


def parse(raw: dict, catalog: Path) -> CatalogEntry:
    """takes raw entry and turns it into a CatalogEntry"""
    midi_path = catalog / raw["midi_path"]
    return CatalogEntry(
        song_id=raw["song_id"],
        title=raw["title"],
        artist=raw["artist"],
        source=raw["source"],
        midi_path=midi_path,
    )


def load_catalog(path: Path) -> list[CatalogEntry]:
    """Checks a catalog file"""

    with open(path, encoding="utf-8") as file:
        raw_entries = json.load(file)
    entries = []
    seen_ids = set()
    for raw in raw_entries:
        entry = parse(raw, path.parent)
        if entry.song_id in seen_ids:
            raise CatalogError(f"Duplicate song_id in catalog: {entry.song_id}")
        seen_ids.add(entry.song_id)
        entries.append(entry)
    return entries
