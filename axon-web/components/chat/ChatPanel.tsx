"use client";

import { useState, useEffect, useRef } from "react";
import { useChatWS } from "@/hooks/useChatWS";
import { useSpeech } from "@/hooks/useSpeech";
import { useTTS } from "@/hooks/useTTS";
import { useAppStore } from "@/lib/store";
import { MessageBubble } from "./MessageBubble";
import { VoiceButton } from "./VoiceButton";
import { AudioPlayer } from "./AudioPlayer";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Send, Loader2, Trash2, Volume2 } from "lucide-react";

export function ChatPanel() {
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { messages, isConnected, sendMessage, clearMessages } = useChatWS();
  const { isListening, transcript, isSupported, startListening, stopListening, resetTranscript } =
    useSpeech();
  const { speak } = useTTS();
  const { speakResponses, setSpeakResponses } = useAppStore();

  useEffect(() => {
    if (transcript) {
      setInput(transcript);
      resetTranscript();
    }
  }, [transcript, resetTranscript]);

  useEffect(() => {
    if (speakResponses && messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.role === "assistant") {
        speak(lastMessage.content, lastMessage.audioUrl);
      }
    }
  }, [messages, speakResponses, speak]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    setIsTyping(true);
    sendMessage(input);
    setInput("");

    setTimeout(() => setIsTyping(false), 1000);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <Label htmlFor="speak-toggle" className="flex items-center gap-2 cursor-pointer">
            <Volume2 className="h-4 w-4" />
            Hablar respuesta
          </Label>
          <Switch
            id="speak-toggle"
            checked={speakResponses}
            onCheckedChange={setSpeakResponses}
          />
        </div>

        <Button variant="outline" size="sm" onClick={clearMessages}>
          <Trash2 className="mr-2 h-4 w-4" />
          Limpiar
        </Button>
      </div>

      <div className="flex-1 overflow-auto rounded-2xl border border-slate-800 bg-slate-950/50 p-6 mb-4 min-h-[400px]">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-slate-400">
            <div className="text-center">
              <p className="text-lg mb-2">No hay mensajes</p>
              <p className="text-sm">Escribe o usa el micrófono para empezar</p>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isTyping && (
              <div className="flex justify-start mb-4">
                <div className="bg-gradient-to-br from-fuchsia-500 to-purple-600 text-white rounded-2xl px-4 py-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-white animate-bounce" />
                    <div className="w-2 h-2 rounded-full bg-white animate-bounce delay-100" />
                    <div className="w-2 h-2 rounded-full bg-white animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="flex gap-3">
        <Input
          placeholder="Escribe tu mensaje o usa el micrófono..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={!isConnected}
          className="flex-1"
        />

        {isSupported && (
          <VoiceButton
            isListening={isListening}
            onStart={startListening}
            onStop={stopListening}
          />
        )}

        <Button
          onClick={handleSend}
          disabled={!input.trim() || !isConnected}
          className="glow-cyan"
        >
          {isConnected ? <Send className="h-4 w-4" /> : <Loader2 className="h-4 w-4 animate-spin" />}
        </Button>
      </div>

      {!isConnected && (
        <p className="text-xs text-yellow-400 mt-2">Conectando al servidor...</p>
      )}

      <AudioPlayer />
    </div>
  );
}
