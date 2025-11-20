"use client";

import { useState, useRef, useEffect } from "react";
import { useApiClient, streamChat } from "@/lib/api";
import { getSocket } from "@/lib/ws";
import { Mic, MicOff, Send, Sparkles, Undo2, Info } from "lucide-react";
import { useToast } from "@/components/Toast";
import { useChatSessions } from "@/lib/hooks/useChatSessions";
import ConversationsSidebar from "@/components/ConversationsSidebar";
import MessageBubble from "@/components/MessageBubble";

interface Message {
  role: string;
  content: string;
  session_url?: string;
  type?: string;
  streaming?: boolean;
  timestamp?: string;
  meta?: Record<string, any>;
}

export default function AgentPage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [undoStack, setUndoStack] = useState<string[]>([]);
  const [isImproving, setIsImproving] = useState(false);
  const [improvementInfo, setImprovementInfo] = useState<{
    changes: string[];
    reasoning: string;
    provider: string;
  } | null>(null);
  const [showImprovementDetails, setShowImprovementDetails] = useState(false);
  const recognitionRef = useRef<any>(null);
  
  const {
    currentSessionId,
    sessions,
    messages: sessionMessages,
    loading: sessionsLoading,
    offline,
    loadSessions,
    createSession,
    saveMessage,
    selectSession,
    setCurrentSessionId,
  } = useChatSessions();

  const [displayMessages, setDisplayMessages] = useState<Message[]>([]);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Ignore
        }
        recognitionRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!currentSessionId) {
      createSession();
    }
  }, [currentSessionId, createSession]);

  useEffect(() => {
    setDisplayMessages(sessionMessages);
  }, [sessionMessages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    if (!currentSessionId) {
      showToast("Creando sesión...", "info");
      return;
    }

    const userInput = input;
    const timestamp = new Date().toISOString();
    const userMsg: Message = { 
      role: "user", 
      content: userInput,
      timestamp 
    };
    
    setInput("");
    setLoading(true);
    setStreaming(true);

    setDisplayMessages((prev) => [...prev, userMsg]);
    await saveMessage(currentSessionId, "user", userInput);

    setDisplayMessages((prev) => [...prev, { 
      role: "assistant", 
      content: "", 
      streaming: true,
      timestamp: new Date().toISOString()
    }]);

    let accumulatedContent = "";

    try {
      await streamChat({
        messages: [{ role: "user", content: userInput }],
        provider: "auto",
        onChunk: (chunk) => {
          accumulatedContent += chunk;
          
          setDisplayMessages((prev) => {
            const updated = [...prev];
            const assistantIndex = updated.length - 1;
            if (updated[assistantIndex] && updated[assistantIndex].role === "assistant") {
              updated[assistantIndex] = {
                ...updated[assistantIndex],
                content: accumulatedContent,
                streaming: true
              };
            }
            return updated;
          });
        },
        onComplete: async () => {
          setDisplayMessages((prev) => {
            const updated = [...prev];
            const assistantIndex = updated.length - 1;
            if (updated[assistantIndex] && updated[assistantIndex].role === "assistant") {
              updated[assistantIndex] = {
                ...updated[assistantIndex],
                streaming: false
              };
            }
            return updated;
          });
          
          if (accumulatedContent) {
            await saveMessage(currentSessionId, "assistant", accumulatedContent, { provider: "auto" });
            loadSessions();
          }
          
          setStreaming(false);
          setLoading(false);
        },
        onError: async (error) => {
          console.error("Streaming error:", error);
          showToast("Usando modo normal...", "info");
          
          try {
            const res = await api.post("/api/agent/chat", { 
              text: userInput,
              session_id: currentSessionId 
            });
            
            const assistantContent = res.data.output;
            
            setDisplayMessages((prev) => {
              const updated = [...prev];
              const assistantIndex = updated.length - 1;
              if (updated[assistantIndex] && updated[assistantIndex].role === "assistant") {
                updated[assistantIndex] = {
                  role: "assistant",
                  content: assistantContent,
                  session_url: res.data.session_url,
                  type: res.data.type,
                  streaming: false,
                  timestamp: new Date().toISOString(),
                  meta: { provider: res.data.provider }
                };
              }
              return updated;
            });
            
            await saveMessage(currentSessionId, "assistant", assistantContent, {
              provider: res.data.provider,
              type: res.data.type,
              session_url: res.data.session_url
            });
            loadSessions();
            
            if (res.data.type === "autonomous_session") {
              showToast("Sesión autónoma iniciada", "success");
            }
            
            setStreaming(false);
            setLoading(false);
          } catch (fallbackError) {
            console.error("Fallback error:", fallbackError);
            showToast("Error al enviar mensaje", "error");
            
            setDisplayMessages((prev) => {
              return prev.filter(msg => !(msg.role === "assistant" && msg.streaming));
            });
            
            setStreaming(false);
            setLoading(false);
          }
        }
      });
    } catch (error) {
      console.error("Chat error:", error);
      showToast("Error al enviar mensaje", "error");
      
      setDisplayMessages((prev) => {
        return prev.filter(msg => !(msg.role === "assistant" && msg.streaming));
      });
      
      setStreaming(false);
      setLoading(false);
    }
  };

  const improveMessage = async () => {
    if (!input.trim()) {
      showToast("Escribe un mensaje primero", "info");
      return;
    }

    setUndoStack([...undoStack, input]);
    setIsImproving(true);
    
    try {
      const res = await api.post("/api/prompt/improve", {
        text: input,
      });

      setInput(res.data.improved);
      setImprovementInfo({
        changes: res.data.changes || [],
        reasoning: res.data.reasoning || "",
        provider: res.data.provider || "unknown",
      });
      
      showToast(`✨ Mensaje mejorado con ${res.data.provider}`, "success");
      
      if (res.data.changes && res.data.changes.length > 0) {
        setShowImprovementDetails(true);
        setTimeout(() => setShowImprovementDetails(false), 5000);
      }
    } catch (error) {
      console.error("Improve error:", error);
      
      setLoading(true);
      try {
        const fallbackRes = await api.post("/api/llm/chat", {
          messages: [
            {
              role: "user",
              content: `Mejora este texto para que sea más claro, profesional y efectivo:\n\n${input}`,
            },
          ],
          provider: "auto",
        });

        setInput(fallbackRes.data.content);
        showToast("Mensaje mejorado (método alternativo)", "success");
      } catch (fallbackError) {
        console.error("Fallback improve error:", fallbackError);
        showToast("Error al mejorar el mensaje", "error");
        setUndoStack(undoStack.slice(0, -1));
      } finally {
        setLoading(false);
      }
    } finally {
      setIsImproving(false);
    }
  };

  const undoImprovement = () => {
    if (undoStack.length > 0) {
      const previous = undoStack[undoStack.length - 1];
      setInput(previous);
      setUndoStack(undoStack.slice(0, -1));
      setImprovementInfo(null);
      setShowImprovementDetails(false);
      showToast("Cambio deshecho", "info");
    }
  };

  const toggleRecording = async () => {
    const hasSpeechAPI = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
    
    if (isRecording) {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          console.error("Error stopping recognition:", e);
        }
        recognitionRef.current = null;
      }
      setIsRecording(false);
      return;
    }

    if (hasSpeechAPI) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.lang = 'es-ES';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsRecording(true);
        showToast("Escuchando...", "info");
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        showToast("Texto capturado", "success");
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        showToast(`Error: ${event.error}`, "error");
        setIsRecording(false);
        recognitionRef.current = null;
      };

      recognition.onend = () => {
        setIsRecording(false);
        recognitionRef.current = null;
      };

      recognitionRef.current = recognition;
      recognition.start();
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const audioChunks: Blob[] = [];
        
        mediaRecorder.ondataavailable = (event) => {
          audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          
          const formData = new FormData();
          formData.append('audio', audioBlob);
          
          try {
            const res = await api.post('/api/agent/stt', formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            });
            setInput(res.data.text);
            showToast("Texto capturado (backend STT)", "success");
          } catch (error) {
            console.error("STT error:", error);
            showToast("Error en transcripción", "error");
          } finally {
            stream.getTracks().forEach(track => track.stop());
          }
        };
        
        setIsRecording(true);
        showToast("Grabando (backend STT)...", "info");
        mediaRecorder.start();
        
        const maxRecordingTime = 30000;
        setTimeout(() => {
          if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
          }
        }, maxRecordingTime);
        
        recognitionRef.current = {
          stop: () => mediaRecorder.stop()
        };
        
      } catch (error) {
        console.error("Microphone error:", error);
        showToast("No se pudo acceder al micrófono", "error");
      }
    }
  };

  const handleNewConversation = () => {
    createSession();
    setDisplayMessages([]);
  };

  const handleSelectSession = (sessionId: string) => {
    selectSession(sessionId);
  };

  return (
    <div className="h-full flex">
      <ConversationsSidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        loading={sessionsLoading}
        offline={offline}
        onSelectSession={handleSelectSession}
        onNewConversation={handleNewConversation}
      />
      
      <div className="flex-1 flex flex-col">
        <div className="p-6 border-b border-border">
          <h1 className="text-3xl font-bold text-cyan-400">Super Axon Agent</h1>
          {currentSessionId && (
            <p className="text-sm text-muted-foreground mt-1">
              Sesión: {currentSessionId.slice(0, 20)}...
            </p>
          )}
        </div>

        <div className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-4xl mx-auto space-y-4">
            {displayMessages.length === 0 ? (
              <div className="text-center text-muted-foreground py-12">
                <p className="text-lg mb-2">¡Bienvenido a Super Axon Agent!</p>
                <p className="text-sm">Comienza una conversación escribiendo un mensaje.</p>
              </div>
            ) : (
              displayMessages.map((msg, idx) => (
                <MessageBubble
                  key={idx}
                  role={msg.role as "user" | "assistant"}
                  content={msg.content}
                  timestamp={msg.timestamp}
                  provider={msg.meta?.provider}
                  streaming={msg.streaming}
                  sessionUrl={msg.session_url}
                  sessionType={msg.type}
                />
              ))
            )}
            {loading && !streaming && (
              <div className="text-center text-muted-foreground animate-pulse">Pensando...</div>
            )}
            {streaming && (
              <div className="text-center text-cyan-400 animate-pulse">Generando respuesta...</div>
            )}
          </div>
        </div>

        <div className="p-6 border-t border-border">
          {showImprovementDetails && improvementInfo && (
            <div className="max-w-4xl mx-auto mb-3 p-4 bg-purple-900/20 border border-purple-500/30 rounded-lg">
              <div className="flex items-start gap-2">
                <Info size={16} className="text-purple-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-purple-300 mb-1">
                    Mejoras aplicadas ({improvementInfo.provider}):
                  </p>
                  <ul className="text-xs text-purple-200 space-y-1 mb-2">
                    {improvementInfo.changes.slice(0, 3).map((change, idx) => (
                      <li key={idx} className="flex items-start gap-1">
                        <span className="text-purple-400">•</span>
                        <span>{change}</span>
                      </li>
                    ))}
                    {improvementInfo.changes.length > 3 && (
                      <li className="text-purple-400">
                        +{improvementInfo.changes.length - 3} más...
                      </li>
                    )}
                  </ul>
                  {improvementInfo.reasoning && (
                    <p className="text-xs text-purple-300/80 italic">
                      {improvementInfo.reasoning}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
          
          <div className="max-w-4xl mx-auto flex gap-2">
            <button
              onClick={toggleRecording}
              className={`p-3 rounded-lg transition-colors ${
                isRecording
                  ? "bg-red-500 hover:bg-red-600 animate-pulse"
                  : "bg-accent hover:bg-accent/80"
              }`}
              title={isRecording ? "Detener grabación" : "Grabar mensaje de voz"}
            >
              {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && !loading && !isImproving && sendMessage()}
              placeholder="Escribe tu mensaje..."
              disabled={loading || isImproving}
              className="flex-1 px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 disabled:opacity-50 transition-all"
            />
            {undoStack.length > 0 && (
              <button
                onClick={undoImprovement}
                disabled={loading || isImproving}
                className="px-4 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-orange-800 disabled:opacity-50 rounded-lg flex items-center gap-2 transition-colors"
                title={`Deshacer (${undoStack.length} cambio${undoStack.length > 1 ? 's' : ''} disponible${undoStack.length > 1 ? 's' : ''})`}
              >
                <Undo2 size={20} />
                Deshacer
              </button>
            )}
            <button
              onClick={improveMessage}
              disabled={loading || isImproving || !input.trim()}
              className={`px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 rounded-lg flex items-center gap-2 transition-colors ${
                isImproving ? "animate-pulse" : ""
              }`}
              title="Mejorar mensaje con IA profesional"
            >
              <Sparkles size={20} className={isImproving ? "animate-spin" : ""} />
              {isImproving ? "Mejorando..." : "Mejorar"}
            </button>
            <button
              onClick={sendMessage}
              disabled={loading}
              className="px-6 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-cyan-700 disabled:opacity-50 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Send size={20} />
              Enviar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
