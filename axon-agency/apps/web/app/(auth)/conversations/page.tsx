"use client";

import { useEffect, useState } from "react";
import { useApiClient } from "@/lib/api";
import { MessageSquare, User, Bot, Filter } from "lucide-react";

export default function ConversationsPage() {
  const api = useApiClient();
  const [conversations, setConversations] = useState<any[]>([]);
  const [sessionFilter, setSessionFilter] = useState("");
  const [sessions, setSessions] = useState<string[]>([]);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const res = await api.get("/api/conversations/list");
      const items = res.data.items || [];
      setConversations(items);
      
      const uniqueSessions = [...new Set(items.map((c: any) => c.session_id))] as string[];
      setSessions(uniqueSessions);
    } catch (error) {
      console.error("Error fetching conversations:", error);
    }
  };

  const filteredConversations = sessionFilter
    ? conversations.filter(c => c.session_id === sessionFilter)
    : conversations;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Conversaciones</h1>
          <p className="text-muted-foreground">Historial de conversaciones con agentes</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <MessageSquare className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Total Mensajes</p>
          </div>
          <p className="text-3xl font-bold">{conversations.length}</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <User className="text-purple-400" size={20} />
            <p className="text-sm font-medium">Sesiones Únicas</p>
          </div>
          <p className="text-3xl font-bold">{sessions.length}</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Bot className="text-green-400" size={20} />
            <p className="text-sm font-medium">Mensajes de IA</p>
          </div>
          <p className="text-3xl font-bold">
            {conversations.filter(c => c.role === 'assistant').length}
          </p>
        </div>
      </div>

      {sessions.length > 0 && (
        <div className="flex items-center gap-3 bg-card p-4 rounded-lg border border-border">
          <Filter className="text-cyan-400" size={20} />
          <select
            value={sessionFilter}
            onChange={(e) => setSessionFilter(e.target.value)}
            className="flex-1 px-4 py-2 bg-accent rounded-lg border border-border focus:border-cyan-500 outline-none"
          >
            <option value="">Todas las sesiones</option>
            {sessions.map((sessionId) => (
              <option key={sessionId} value={sessionId}>
                Sesión: {sessionId.slice(0, 8)}...
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="space-y-4">
        {filteredConversations.map((conversation) => (
          <div
            key={conversation.id}
            className={`p-4 rounded-lg border ${
              conversation.role === 'user'
                ? 'bg-cyan-500/10 border-cyan-500/20 ml-8'
                : 'bg-purple-500/10 border-purple-500/20 mr-8'
            }`}
          >
            <div className="flex items-start gap-3">
              <div className={`p-2 rounded-full ${
                conversation.role === 'user' ? 'bg-cyan-500/20' : 'bg-purple-500/20'
              }`}>
                {conversation.role === 'user' ? (
                  <User size={16} className="text-cyan-400" />
                ) : (
                  <Bot size={16} className="text-purple-400" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-medium capitalize">{conversation.role}</span>
                  <span className="text-xs text-muted-foreground">
                    {new Date(conversation.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-sm whitespace-pre-wrap">{conversation.content}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredConversations.length === 0 && (
        <div className="bg-card p-12 rounded-lg border border-border text-center">
          <MessageSquare className="mx-auto mb-4 text-muted-foreground" size={48} />
          <p className="text-muted-foreground">No hay conversaciones disponibles</p>
        </div>
      )}
    </div>
  );
}
