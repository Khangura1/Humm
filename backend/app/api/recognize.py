"""The recognition routes: list the songs, and recognize a hum"""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel

from app.audio import check_upload, decode_audio
from app.config import get_settings
from matching.config import AudioEngineConfig
from matching.errors import NotEnoughAudioError
from matching.pipeline import analyze

router = APIRouter(prefix="/api")
ENGINE_CONFIG = AudioEngineConfig()


class SongOut(BaseModel):
    """One song the app knows"""

    song_id: str
    title: str
    artist: str


class MatchOut(BaseModel):
    """One of the top matches for a hum"""

    song_id: str
    title: str
    artist: str
    similarity_score: float


class RecognitionOut(BaseModel):
    """Everything sent back after recognizing a hum"""

    duration_s: float
    matches: list[MatchOut]


@router.get("/songs")
def list_songs(request: Request) -> list[SongOut]:
    """Every song in the catalog, so the page can show what it knows"""
    songs = []
    for entry in request.app.state.catalog.values():
        songs.append(
            SongOut(song_id=entry.song_id, title=entry.title, artist=entry.artist)
        )
    return songs


@router.post("/recognize")
def recognize(request: Request, audio: Annotated[UploadFile, File()]) -> RecognitionOut:
    """Turn an uploaded recording into the top matching songs"""
    settings = get_settings()
    audio_bytes = audio.file.read(settings.max_upload_bytes + 1)
    check_upload(audio.content_type, len(audio_bytes), settings.max_upload_bytes)

    sample_rate_hz = ENGINE_CONFIG.pitch.sample_rate_hz
    signal = decode_audio(audio_bytes, sample_rate_hz, settings.ffmpeg_timeout_s)
    try:
        analysis = analyze(
            signal, sample_rate_hz, request.app.state.index, ENGINE_CONFIG
        )
    except NotEnoughAudioError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    catalog = request.app.state.catalog
    matches = []
    for match in analysis.matches:
        entry = catalog[match.song_id]
        matches.append(
            MatchOut(
                song_id=match.song_id,
                title=entry.title,
                artist=entry.artist,
                similarity_score=round(match.similarity_score, 3),
            )
        )
    return RecognitionOut(duration_s=round(analysis.duration_s, 1), matches=matches)
