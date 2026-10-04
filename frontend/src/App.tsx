import { useEffect, useRef, useState } from "react";
import { postForm, request } from "./api/client";
import Hummingbird from "./components/Hummingbird";
import Waveform from "./components/Waveform";

type Status = "checking" | "healthy" | "unhealthy";
type Phase = "idle" | "recording" | "matching" | "done" | "error";

type HealthResponse = {
  status: string;
};

type Match = {
  song_id: string;
  title: string;
  artist: string;
  similarity_score: number;
};

type RecognitionResponse = {
  duration_s: number;
  matches: Match[];
};

const MESSAGES: Record<Status, string> =
{
  checking: "Checking the API...",
  healthy: "Ready to listen",
  unhealthy: "Server is waking up, try again in a minute",
};

const MAX_RECORDING_MS = 15000;

export default function App()
{
  const [status, setStatus] = useState<Status>("checking");
  const [phase, setPhase] = useState<Phase>("idle");
  const [match, setMatch] = useState<Match | null>(null);
  const [error, setError] = useState("");
  const [stream, setStream] = useState<MediaStream | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const timeoutRef = useRef<number | undefined>(undefined);

  useEffect(() =>
  {
    request<HealthResponse>("/api/health")
      .then(() => setStatus("healthy"))
      .catch(() => setStatus("unhealthy"));
  }, []);

  async function recognize(blob: Blob)
  {
    setPhase("matching");
    const form = new FormData();
    form.append("audio", blob, "hum");
    try
    {
      const result = await postForm<RecognitionResponse>("/api/recognize", form);
      if (result.matches.length === 0)
      {
        throw new Error("No song matched that hum. Try again.");
      }
      setMatch(result.matches[0]);
      setPhase("done");
    }
    catch (err)
    {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setPhase("error");
    }
  }

  async function startRecording()
  {
    setMatch(null);
    setError("");
    let stream: MediaStream;
    try
    {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    }
    catch
    {
      setError("Microphone access was blocked. Allow it and try again.");
      setPhase("error");
      return;
    }

    const recorder = new MediaRecorder(stream);
    const chunks: Blob[] = [];
    recorder.ondataavailable = (event) => chunks.push(event.data);
    recorder.onstop = () =>
    {
      window.clearTimeout(timeoutRef.current);
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
      void recognize(new Blob(chunks, { type: recorder.mimeType }));
    };
    recorderRef.current = recorder;
    recorder.start();
    setStream(stream);
    setPhase("recording");
    timeoutRef.current = window.setTimeout(() => recorder.stop(), MAX_RECORDING_MS);
  }

  function stopRecording()
  {
    recorderRef.current?.stop();
  }

  return (
    <main className="app">
      <header className="brand">
        <Hummingbird className="logo" size={88} />
        <h1>Humm</h1>
        <p className="tagline">Getting songs out of your head</p>
      </header>

      <section className="card">
        <p className={`status ${status}`}>
          <span className="dot" aria-hidden="true" />
          {MESSAGES[status]}
        </p>

        <Waveform stream={stream} />

        <p className="hint">
          {phase === "recording"
            ? "Listening... hum the part you remember"
            : "Hum a song for 5 to 15 seconds and Humm will guess what it is."}
        </p>

        {phase === "recording" ? (
          <button className="record recording" onClick={stopRecording}>
            Stop and find my song
          </button>
        ) : (
          <button
            className="record"
            onClick={() => void startRecording()}
            disabled={phase === "matching"}
          >
            {phase === "matching" ? "Finding your song..." : "Start humming"}
          </button>
        )}

        {phase === "done" && match && (
          <div className="result">
            <p className="label">Closest match</p>
            <h2>{match.title}</h2>
            <p className="artist">{match.artist}</p>
            <div className="meter" aria-hidden="true">
              <span style={{ width: `${Math.round(match.similarity_score * 100)}%` }} />
            </div>
            <p className="score">{Math.round(match.similarity_score * 100)}% similar</p>
          </div>
        )}

        {phase === "error" && <p className="error">{error}</p>}
      </section>
    </main>
  );
}
