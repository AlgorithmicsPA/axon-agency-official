"use client";

import { formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";
import { MessageSquarePlus, WifiOff, Loader2 } from "lucide-react";
import { Session } from "@/lib/hooks/useChatSessions";

interface ConversationsSidebarProps {
  sessions: Session[];
  currentSessionId: string | null;
  loading: boolean;
  offline: boolean;
  onSelectSession: (sessionId: string) => void;
  onNewConversation: () => void;
}

export default function ConversationsSidebar({
  sessions,
  currentSessionId,
  loading,
  offline,
  onSelectSession,
  onNewConversation,
}: ConversationsSidebarProps) {
  const formatRelativeTime = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), {
        addSuffix: true,
        locale: es,
      });
    } catch (error) {
      return "ahora";
    }
  };

  return (
    <div className="w-80 h-full bg-card border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-cyan-400">Conversaciones</h2>
          {offline && (
            <div className="flex items-center gap-1 text-xs text-yellow-500 bg-yellow-500/10 px-2 py-1 rounded">
              <WifiOff size={12} />
              <span>Offline</span>
            </div>
          )}
        </div>
        
        <button
          onClick={onNewConversation}
          className="w-full px-4 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          <MessageSquarePlus size={18} />
          <span className="font-medium">Nueva Conversación</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading && sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
            <Loader2 className="animate-spin mb-2" size={24} />
            <span className="text-sm">Cargando conversaciones...</span>
          </div>
        ) : sessions.length === 0 ? (
          <div className="p-4 text-center text-muted-foreground">
            <p className="text-sm">No hay conversaciones aún.</p>
            <p className="text-xs mt-2">Crea una nueva conversación para comenzar.</p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {sessions.map((session) => {
              const isActive = session.session_id === currentSessionId;
              
              return (
                <div
                  key={session.session_id}
                  onClick={() => onSelectSession(session.session_id)}
                  className={`p-4 cursor-pointer transition-all hover:bg-accent/50 ${
                    isActive ? "bg-accent border-l-4 border-l-cyan-500" : ""
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <h3
                      className={`font-medium text-sm line-clamp-2 flex-1 ${
                        isActive ? "text-cyan-400" : "text-foreground"
                      }`}
                    >
                      {session.title || "Nueva conversación"}
                    </h3>
                  </div>
                  
                  <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                    {session.last_message_preview || "Sin mensajes"}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">
                      {formatRelativeTime(session.last_message_at)}
                    </span>
                    
                    {session.last_message_role && (
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          session.last_message_role === "user"
                            ? "bg-blue-500/20 text-blue-400"
                            : "bg-purple-500/20 text-purple-400"
                        }`}
                      >
                        {session.last_message_role === "user" ? "Tú" : "IA"}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
