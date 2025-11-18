"use client";

import { useEffect, useRef } from "react";

interface AudioPlayerProps {
  audioUrl?: string;
  autoPlay?: boolean;
}

export function AudioPlayer({ audioUrl, autoPlay = true }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioUrl && audioRef.current && autoPlay) {
      audioRef.current.play().catch((err) => {
        console.error("Audio playback failed:", err);
      });
    }
  }, [audioUrl, autoPlay]);

  if (!audioUrl) return null;

  return <audio ref={audioRef} src={audioUrl} className="hidden" />;
}
