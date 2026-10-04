# Humm — Hum-to-Search Song Recognition

A web app that names the song stuck in your head: hum it into your browser, and Humm's from-scratch signal processing engine finds the closest match.

### ▶ [Try Humm](https://humm-gamma.vercel.app))


> The backend runs on Render's free tier, which sleeps when idle. If the page says the server is waking up, give it about a minute.

## Overview

Humm is a query-by-humming app. You hum a tune for 5 to 15 seconds, and it tells you which song it is. It doesn't matter what key you hum in, or whether you hum faster or slower than the original: Humm compares the *shape* of your melody, not the exact notes.

The recognition engine is written by hand in Python and NumPy, from parsing the WAV file to the final ranking. It covers pitch tracking with the YIN algorithm, key-free melody contours, and subsequence dynamic time warping, with no machine learning. The only library in the audio path reads MIDI files.

## How it works

```mermaid
flowchart LR
    A[Browser records hum] --> B[ffmpeg: 16 kHz mono WAV]
    B --> C[WAV parser]
    C --> D[YIN pitch tracking]
    D --> E[Voicing]
    E --> F[Key-free melody shape]
    F --> G[Subsequence DTW vs every song]
    G --> H[Best match + score]
```

1. The browser records your hum with the `MediaRecorder` API and uploads it to the server.
2. ffmpeg converts the recording (webm from Chrome and Firefox, mp4 from Safari) into 16 kHz mono WAV, which a hand-written parser reads into samples.
3. YIN measures your pitch 100 times a second, and frames without real humming (breaths, pauses, noise) are dropped.
4. The pitches become a key-free melody shape: converted to semitones, centered on the median, smoothed with a median filter, and capped at one octave.
5. Subsequence DTW lines that shape up against every song, letting your hum start anywhere in the song and run up to twice as fast or slow.
6. The closest song comes back with a similarity score

## Features

- 🎙️ **Record in the browser** — one tap, stops automatically at 15 seconds
- 〰️ **Live waveform** — see your hum as you record
- 🎼 **Key-free matching** — hum in any key, at any reasonable speed
- 🎯 **Partial hums** — hum the chorus, the opening, or anything in between
- 🧮 **From-scratch engine** — WAV parser, YIN, median filter and DTW all hand-written
- 🎵 **14 songs** — all public domain, generated from note lists by a script
- ☁️ **Deployed** — FastAPI on Render (Docker), React on Vercel

## Songs it knows

Amazing Grace · Bridal Chorus (Here Comes the Bride) · Für Elise · Happy Birthday to You · In the Hall of the Mountain King · Jingle Bells (chorus) · London Bridge Is Falling Down · Mary Had a Little Lamb · Ode to Joy · Old MacDonald Had a Farm · Row, Row, Row Your Boat · Silent Night · Twinkle Twinkle Little Star · We Wish You a Merry Christmas

**Tip:** hum the famous part 

## Repository structure

```
Humm/
├── backend/
│   ├── app/                     # FastAPI web app
│   │   ├── api/                 #   routes: health, songs, recognize
│   │   ├── audio.py             #   upload checks + ffmpeg conversion
│   │   ├── config.py            #   settings from environment variables
│   │   └── main.py              #   app setup, loads catalog + index at startup
│   ├── matching/                # Recognition engine (no web code)
│   │   ├── wav.py               #   WAV parser and writer
│   │   ├── pitch.py             #   YIN pitch tracking + voicing
│   │   ├── contour.py           #   Hz → MIDI, melody-shape normalization
│   │   ├── melody.py            #   MIDI → note-per-frame arrays
│   │   ├── catalog.py           #   reads data/catalog.json
│   │   ├── index.py             #   every song's shape, saved to index.npz
│   │   ├── dtw.py               #   subsequence dynamic time warping
│   │   ├── search.py            #   ranks songs against a hum
│   │   └── pipeline.py          #   analyze(): recording in, match out
│   ├── scripts/
│   │   ├── make_midi.py         #   writes the reference MIDI files
│   │   └── build_index.py       #   builds data/index.npz
│   ├── data/                    # catalog.json + MIDI files
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── App.tsx              # recording flow + results
│       ├── api/client.ts        # all requests to the backend
│       └── components/          # Waveform, Hummingbird logo
├── .github/workflows/ci.yml     # lint, format, type checks, build
└── README.md
```

## Tech stack

| Layer | Technology |
|---|---|
| Engine | Python 3.13 · NumPy · pretty_midi (MIDI reading only) |
| Backend | FastAPI · Pydantic · Uvicorn · ffmpeg · Docker |
| Frontend | React 19 · TypeScript · Vite · MediaRecorder / Web Audio |
| Hosting | Render (backend) · Vercel (frontend) |
| Tooling | GitHub Actions · ruff · mypy · oxlint |

## Design choices

| Choice | Why |
|---|---|
| Classic signal processing, not ML | Every step is explainable and debuggable, and no training data is needed. |
| Plain-Python DTW, no Numba | Readability first. It's fast enough for 14 songs, and compiling the DTW loop is the first speed-up if the catalog grows. |
| Melodies generated by a script | `make_midi.py` makes songs reproducible and reviewable: a wrong note is a one-word fix. |
| One famous section per song | Key normalization uses the whole song's median, so songs whose sections sit in different ranges (like the Jingle Bells verse) are trimmed to their most-hummed part. |
| Index built at deploy time | `index.npz` always matches the MIDI files, and no generated binary is committed. |

**Known limitations:** matching time grows with the catalog, similar-shaped songs (*Mary Had a Little Lamb* and *Ode to Joy*) can score close together, and there are no automated tests yet. Each stage was verified by hand with pitch plots and recordings of real humming.

## Build & run

Requires Python 3.13, Node.js 24, and ffmpeg (`brew install ffmpeg` on a Mac).

### 🐍 Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m scripts.build_index
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000, with interactive docs at http://localhost:8000/docs.

### ⚛️ Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. In development, the app talks to the local backend automatically.

### 🎵 Adding a song

1. Add the melody to `SONGS` in `backend/scripts/make_midi.py` as `NOTE:BEATS` (e.g. `E4 E4 F4 G4:2`).
2. Add a matching entry to `backend/data/catalog.json`.
3. Rebuild: `python -m scripts.make_midi && python -m scripts.build_index`
4. Open the new `.mid` file in MuseScore and listen to check the notes.

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | `{"status": "ok"}` when the server is up |
| GET | `/api/songs` | Every song in the catalog |
| POST | `/api/recognize` | Upload an `audio` file; returns the best match and its score |

Errors come back as `{"detail": "..."}`: `413` (over 5 MB), `415` (not audio), `422` (unreadable, too short, or too quiet).

## Acknowledgments

YIN algorithm: A. de Cheveigné and H. Kawahara, "YIN, a fundamental frequency estimator for speech and music," *JASA*, 2002. Licensed under [MIT](LICENSE).
