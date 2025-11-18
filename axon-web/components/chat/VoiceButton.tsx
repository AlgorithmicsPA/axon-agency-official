"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Mic, MicOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface VoiceButtonProps {
  isListening: boolean;
  onStart: () => void;
  onStop: () => void;
}

export function VoiceButton({ isListening, onStart, onStop }: VoiceButtonProps) {
  const [level, setLevel] = useState(0);

  useEffect(() => {
    if (isListening) {
      const interval = setInterval(() => {
        setLevel(Math.random() * 100);
      }, 100);
      return () => clearInterval(interval);
    } else {
      setLevel(0);
    }
  }, [isListening]);

  return (
    <div className="relative">
      <Button
        size="icon"
        variant={isListening ? "destructive" : "secondary"}
        onClick={isListening ? onStop : onStart}
        className={cn("h-12 w-12 rounded-full", isListening && "glow-magenta animate-pulse")}
      >
        {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
      </Button>

      {isListening && (
        <div className="absolute -bottom-6 left-0 right-0 flex justify-center gap-1">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-fuchsia-400 rounded-full transition-all"
              style={{
                height: `${Math.max(4, (level * (i + 1)) / 100)}px`,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
