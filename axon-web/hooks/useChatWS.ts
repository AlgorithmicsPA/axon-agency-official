"use client";

import { useEffect, useState, useCallback } from "react";
import { useSocket } from "@/lib/ws-context";
import type { ChatMessage } from "@/lib/types";

export function useChatWS() {
  const socket = useSocket();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!socket) return;

    socket.on("connect", () => {
      setIsConnected(true);
    });

    socket.on("disconnect", () => {
      setIsConnected(false);
    });

    socket.on("chat:assistant", (data: { text: string; audio_url?: string }) => {
      const message: ChatMessage = {
        id: Date.now().toString(),
        role: "assistant",
        content: data.text,
        timestamp: Date.now(),
        audioUrl: data.audio_url,
      };
      setMessages((prev) => [...prev, message]);
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("chat:assistant");
    };
  }, [socket]);

  const sendMessage = useCallback(
    (text: string) => {
      if (!socket) return;
      
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: "user",
        content: text,
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, userMessage]);

      socket.emit("chat:user", { text });
    },
    [socket]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return {
    messages,
    isConnected,
    sendMessage,
    clearMessages,
  };
}
