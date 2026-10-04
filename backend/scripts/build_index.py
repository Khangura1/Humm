"""Build data/index.npz from the catalog
run from backend/: python -m scripts.build_index"""

from pathlib import Path

from matching.catalog import load_catalog
from matching.config import MatchConfig, PitchConfig
from matching.index import MelodyIndex

DATA_DIR = Path(__file__).parent.parent / "data"


def main() -> None:
    entries = load_catalog(DATA_DIR / "catalog.json")
    index = MelodyIndex.build(entries, PitchConfig(), MatchConfig())
    index.save(DATA_DIR / "index.npz")
    print(f"Saved {len(index.contours)} songs to {DATA_DIR / 'index.npz'}")
    for song_id, contour in index.contours.items():
        print(f"  {song_id}: {len(contour)} values")


if __name__ == "__main__":
    main()
