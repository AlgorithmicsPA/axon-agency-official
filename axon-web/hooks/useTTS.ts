"use client";

import { useState, useCallback, useEffect } from "react";

export function useTTS() {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsSupported("speechSynthesis" in window);
    }
  }, []);

  const speak = useCallback(
    (text: string, audioUrl?: string) => {
      if (audioUrl) {
        const audio = new Audio(audioUrl);
        setIsSpeaking(true);
        audio.play();
        audio.onended = () => setIsSpeaking(false);
        return;
      }

      if (!isSupported) {
        console.warn("Text-to-speech not supported");
        return;
      }

      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = "es-ES";
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
    },
    [isSupported]
  );

  const stop = useCallback(() => {
    if (isSupported) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  }, [isSupported]);

  return {
    isSpeaking,
    isSupported,
    speak,
    stop,
  };
}
