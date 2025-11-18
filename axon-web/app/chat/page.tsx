"use client";

import { ChatPanel } from "@/components/chat/ChatPanel";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageSquare, Mic, Volume2 } from "lucide-react";

export default function Chat() {
  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold text-glow-magenta flex items-center gap-3">
          <MessageSquare className="h-8 w-8" />
          Chat & Voice
        </h1>
        <p className="text-slate-400 mt-2">
          Conversa con el agente por texto o voz
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <MessageSquare className="h-4 w-4 text-cyan-400" />
              Texto
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-400">
              Escribe mensajes y recibe respuestas en tiempo real
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Mic className="h-4 w-4 text-fuchsia-400" />
              Voz
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-400">
              Usa el micrófono para dictar mensajes con Web Speech API
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Volume2 className="h-4 w-4 text-green-400" />
              TTS
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-400">
              Activa "Hablar respuesta" para escuchar las respuestas del agente
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="glow-magenta">
        <CardHeader>
          <CardTitle>Panel de Chat</CardTitle>
          <CardDescription>
            Interactúa con el agente usando texto o voz
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[600px]">
          <ChatPanel />
        </CardContent>
      </Card>
    </div>
  );
}
