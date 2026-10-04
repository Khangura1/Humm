import { useEffect, useRef } from "react";

type WaveformProps = {
  stream: MediaStream | null; // the live mic, or null when not recording
};

const HEIGHT = 120;

// Reads a colour from the CSS variables so the wave matches the theme
function cssColor(name: string): string 
{
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

// Draws the mic's sound wave. Dim and gently moving when idle, lit up while recording
export default function Waveform({ stream }: WaveformProps) 
{
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => 
  {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) 
    {
      return;
    }

    let analyser: AnalyserNode | null = null;
    let audioContext: AudioContext | null = null;
    if (stream) 
    {
      audioContext = new AudioContext();
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      audioContext.createMediaStreamSource(stream).connect(analyser);
    }
    const samples = new Float32Array(2048);
    const idleColor = cssColor("--wave-idle");
    const liveColor = cssColor("--wave-live");
    let frame = 0;

    function draw(time: number) 
    {
      if (!canvas || !ctx) 
      {
        return;
      }
      // match the canvas to its on-screen size, sharp on retina screens
      const scale = window.devicePixelRatio || 1;
      const width = canvas.clientWidth;
      if (canvas.width !== width * scale) 
      {
        canvas.width = width * scale;
        canvas.height = HEIGHT * scale;
      }
      ctx.setTransform(scale, 0, 0, scale, 0, 0);
      ctx.clearRect(0, 0, width, HEIGHT);

      const middle = HEIGHT / 2;
      ctx.beginPath();
      if (analyser) 
      {
        analyser.getFloatTimeDomainData(samples);
        for (let x = 0; x <= width; x++) 
        {
          const sample = samples[Math.floor((x / width) * (samples.length - 1))];
          const y = middle + Math.max(-1, Math.min(1, sample * 4)) * (middle - 6);
          if (x === 0) 
          {
            ctx.moveTo(x, y);
          }
          else 
          {
            ctx.lineTo(x, y);
          }
        }
        ctx.strokeStyle = liveColor;
        ctx.lineWidth = 3;
        ctx.shadowColor = liveColor;
        ctx.shadowBlur = 18;
      }
      else 
      {
        // a soft resting wave so the page never looks empty
        for (let x = 0; x <= width; x++) 
        {
          const fade = Math.sin((x / width) * Math.PI);
          const y = middle + Math.sin(x / 22 + time / 600) * 10 * fade;
          if (x === 0) 
          {
            ctx.moveTo(x, y);
          }
          else 
          {
            ctx.lineTo(x, y);
          }
        }
        ctx.strokeStyle = idleColor;
        ctx.lineWidth = 2;
        ctx.shadowBlur = 0;
      }
      ctx.stroke();
      frame = requestAnimationFrame(draw);
    }

    frame = requestAnimationFrame(draw);
    return () => 
    {
      cancelAnimationFrame(frame);
      void audioContext?.close();
    };
  }, [stream]);

  return (
    <div className={stream ? "wave live" : "wave"}>
      <canvas ref={canvasRef} style={{ height: HEIGHT }} aria-hidden="true" />
    </div>
  );
}