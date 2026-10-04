FROM python:3.13-slim

# ffmpeg converts browser recordings (webm/ogg/mp4) into WAV
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# index.npz is gitignored, so build it from the MIDI files on every deploy
RUN python -m scripts.build_index

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]