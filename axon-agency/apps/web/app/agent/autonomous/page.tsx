"use client";

import { useState, useEffect } from "react";
import { useApiClient } from "@/lib/api";
import { 
  Play, 
  Square, 
  Activity, 
  TrendingUp, 
  CheckCircle, 
  XCircle,
  Clock,
  Zap,
  BarChart3,
  AlertTriangle,
  ChevronDown,
  ChevronUp
} from "lucide-react";
import Link from "next/link";
import { StatsCharts } from "./components/StatsCharts";
import { useToast } from "@/components/Toast";
import { useConfirm } from "@/components/ConfirmModal";

interface Session {
  session_id: string;
  status: string;
  mode: string;
  iteration: string;
  improvements_attempted: number;
  improvements_succeeded: number;
  improvements_failed: number;
  success_rate: number;
  last_action: string | null;
  started_at: string;
  errors: string[];
  current_iteration_details?: {
    iteration_number: number;
    phase: string;
    opportunity: any;
    status: string;
  };
}

interface GlobalStats {
  total_sessions: number;
  total_improvements_attempted: number;
  total_improvements_succeeded: number;
  overall_success_rate: number;
  success_rate_by_improvement_type: Record<string, number>;
  success_rate_by_mode: Record<string, number>;
  avg_iterations_per_session: number;
}

export default function AutonomousDashboard() {
  const api = useApiClient();
  const { showToast } = useToast();
  const { confirm } = useConfirm();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [stats, setStats] = useState<GlobalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [startingSession, setStartingSession] = useState(false);
  const [selectedMode, setSelectedMode] = useState("balanced");
  const [maxIterations, setMaxIterations] = useState(10);
  const [showCharts, setShowCharts] = useState(false);

  const loadData = async () => {
    try {
      const [sessionsRes, statsRes] = await Promise.all([
        api.get("/api/agent/autonomous/sessions"),
        api.get("/api/agent/autonomous/stats")
      ]);
      setSessions(sessionsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000);
    return () => clearInterval(interval);
  }, []);

  const startSession = async () => {
    setStartingSession(true);
    try {
      await api.post("/api/agent/autonomous/start", {
        mode: selectedMode,
        max_iterations: maxIterations
      });
      await loadData();
    } catch (error: any) {
      showToast(error.response?.data?.detail || "Error al iniciar sesión", "error");
    } finally {
      setStartingSession(false);
    }
  };

  const stopSession = async (sessionId: string) => {
    const confirmed = await confirm({
      title: "Confirmar detener sesión",
      message: "¿Detener esta sesión autónoma?",
      variant: "warning"
    });
    if (!confirmed) return;
    
    try {
      await api.post(`/api/agent/autonomous/sessions/${sessionId}/stop`);
      await loadData();
    } catch (error: any) {
      showToast(error.response?.data?.detail || "Error al detener sesión", "error");
    }
  };

  const getModeColor = (mode: string) => {
    const colors: Record<string, string> = {
      conservative: "bg-green-500/20 text-green-400 border-green-500/50",
      balanced: "bg-cyan-500/20 text-cyan-400 border-cyan-500/50",
      aggressive: "bg-orange-500/20 text-orange-400 border-orange-500/50",
      exploratory: "bg-purple-500/20 text-purple-400 border-purple-500/50"
    };
    return colors[mode] || "bg-gray-500/20 text-gray-400 border-gray-500/50";
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      running: "text-green-400",
      completed: "text-cyan-400",
      stopped: "text-orange-400",
      failed: "text-red-400"
    };
    return colors[status] || "text-gray-400";
  };

  const getPhaseEmoji = (phase: string) => {
    const emojis: Record<string, string> = {
      introspecting: "🔍",
      predicting: "🎯",
      council_review: "👥",
      architect_review: "🏛️",
      executing: "⚙️",
      learning: "📚"
    };
    return emojis[phase] || "⏳";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Activity className="animate-spin text-cyan-400" size={48} />
      </div>
    );
  }

  const activeSessions = sessions.filter(s => s.status === "running");

  return (
    <div className="h-full flex flex-col space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Agente Autónomo</h1>
          <p className="text-muted-foreground mt-1">Sistema de Auto-Mejora Continua</p>
        </div>
        
        <div className="flex items-center gap-4">
          {activeSessions.length > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 rounded-lg border border-green-500/50">
              <Activity className="animate-pulse text-green-400" size={20} />
              <span className="text-green-400 font-semibold">
                {activeSessions.length} Sesión{activeSessions.length > 1 ? "es" : ""} Activa{activeSessions.length > 1 ? "s" : ""}
              </span>
            </div>
          )}
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Sesiones</p>
                <p className="text-2xl font-bold text-cyan-400">{stats.total_sessions}</p>
              </div>
              <Activity className="text-cyan-500/50" size={32} />
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Mejoras Totales</p>
                <p className="text-2xl font-bold text-purple-400">{stats.total_improvements_attempted}</p>
              </div>
              <Zap className="text-purple-500/50" size={32} />
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Tasa de Éxito</p>
                <p className="text-2xl font-bold text-green-400">
                  {(stats.overall_success_rate * 100).toFixed(1)}%
                </p>
              </div>
              <TrendingUp className="text-green-500/50" size={32} />
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Promedio Iteraciones</p>
                <p className="text-2xl font-bold text-orange-400">
                  {stats.avg_iterations_per_session.toFixed(1)}
                </p>
              </div>
              <BarChart3 className="text-orange-500/50" size={32} />
            </div>
          </div>
        </div>
      )}

      {stats && (
        <div className="flex justify-center">
          <button
            onClick={() => setShowCharts(!showCharts)}
            className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-600 hover:to-purple-600 rounded-lg flex items-center gap-3 font-semibold text-white shadow-lg hover:shadow-xl transition-all"
          >
            <BarChart3 size={20} />
            {showCharts ? "Ocultar Estadísticas" : "Ver Estadísticas Detalladas"}
            {showCharts ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
        </div>
      )}

      {showCharts && stats && (
        <div className="animate-in slide-in-from-top duration-300">
          <StatsCharts stats={stats} />
        </div>
      )}

      <div className="bg-card border border-border rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Iniciar Nueva Sesión Autónoma</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm text-muted-foreground mb-2">Modo de Operación</label>
            <select
              value={selectedMode}
              onChange={(e) => setSelectedMode(e.target.value)}
              className="w-full px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="conservative">🛡️ Conservative (80%+)</option>
              <option value="balanced">⚖️ Balanced (60%+)</option>
              <option value="aggressive">🚀 Aggressive (40%+)</option>
              <option value="exploratory">🔬 Exploratory (0%+)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm text-muted-foreground mb-2">Máx. Iteraciones</label>
            <input
              type="number"
              value={maxIterations}
              onChange={(e) => setMaxIterations(parseInt(e.target.value) || 10)}
              min={1}
              max={100}
              className="w-full px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
            />
          </div>

          <div className="flex items-end">
            <button
              onClick={startSession}
              disabled={startingSession || activeSessions.length > 0}
              className="w-full px-6 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-cyan-700 disabled:opacity-50 rounded-lg flex items-center justify-center gap-2 font-semibold"
            >
              <Play size={20} />
              {startingSession ? "Iniciando..." : "Iniciar Sesión"}
            </button>
          </div>
        </div>

        {activeSessions.length > 0 && (
          <div className="mt-4 p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
            <p className="text-sm text-orange-400">
              ⚠️ Ya hay {activeSessions.length} sesión{activeSessions.length > 1 ? "es" : ""} activa{activeSessions.length > 1 ? "s" : ""}. 
              Detén la{activeSessions.length > 1 ? "s" : ""} sesión{activeSessions.length > 1 ? "es" : ""} activa{activeSessions.length > 1 ? "s" : ""} antes de iniciar una nueva.
            </p>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-auto">
        <h2 className="text-xl font-semibold mb-4">Sesiones Recientes</h2>
        
        {sessions.length === 0 ? (
          <div className="bg-card border border-border rounded-lg p-12 text-center">
            <Activity className="mx-auto text-muted-foreground mb-4" size={64} />
            <p className="text-muted-foreground">No hay sesiones autónomas todavía</p>
            <p className="text-sm text-muted-foreground mt-2">Inicia una nueva sesión para comenzar</p>
          </div>
        ) : (
          <div className="space-y-4">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                className="bg-card border border-border rounded-lg p-6 hover:border-cyan-500/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Link
                        href={`/agent/autonomous/${session.session_id}`}
                        className="text-lg font-semibold text-cyan-400 hover:text-cyan-300"
                      >
                        {session.session_id.slice(0, 8)}...
                      </Link>
                      
                      <span className={`px-3 py-1 rounded-full border text-xs font-semibold ${getModeColor(session.mode)}`}>
                        {session.mode.toUpperCase()}
                      </span>
                      
                      <span className={`font-semibold ${getStatusColor(session.status)}`}>
                        {session.status.toUpperCase()}
                      </span>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock size={14} />
                        {new Date(session.started_at).toLocaleString('es-ES')}
                      </span>
                      <span>{session.iteration}</span>
                    </div>
                  </div>

                  {session.status === "running" && (
                    <button
                      onClick={() => stopSession(session.session_id)}
                      className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg flex items-center gap-2 border border-red-500/50"
                    >
                      <Square size={16} />
                      Detener
                    </button>
                  )}
                </div>

                {session.current_iteration_details && (
                  <div className="mb-4 p-4 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">{getPhaseEmoji(session.current_iteration_details.phase)}</span>
                      <span className="font-semibold text-cyan-400">
                        Fase Actual: {session.current_iteration_details.phase.replace(/_/g, ' ').toUpperCase()}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {typeof session.current_iteration_details.opportunity === 'string' 
                        ? session.current_iteration_details.opportunity 
                        : session.current_iteration_details.opportunity?.description || session.current_iteration_details.status}
                    </p>
                  </div>
                )}

                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="flex items-center gap-2">
                    <Zap className="text-purple-400" size={18} />
                    <div>
                      <p className="text-xs text-muted-foreground">Intentadas</p>
                      <p className="text-lg font-bold">{session.improvements_attempted}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <CheckCircle className="text-green-400" size={18} />
                    <div>
                      <p className="text-xs text-muted-foreground">Exitosas</p>
                      <p className="text-lg font-bold text-green-400">{session.improvements_succeeded}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <XCircle className="text-red-400" size={18} />
                    <div>
                      <p className="text-xs text-muted-foreground">Fallidas</p>
                      <p className="text-lg font-bold text-red-400">{session.improvements_failed}</p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="text-cyan-400" size={18} />
                    <span className="text-sm text-muted-foreground">Tasa de Éxito:</span>
                    <span className="font-bold text-cyan-400">
                      {(session.success_rate * 100).toFixed(1)}%
                    </span>
                  </div>

                  <Link
                    href={`/agent/autonomous/${session.session_id}`}
                    className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg text-sm font-semibold"
                  >
                    Ver Detalles →
                  </Link>
                </div>

                {session.errors.length > 0 && (
                  <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <AlertTriangle className="text-red-400" size={16} />
                      <span className="text-sm font-semibold text-red-400">Errores:</span>
                    </div>
                    {session.errors.slice(0, 3).map((error, idx) => (
                      <p key={idx} className="text-xs text-red-300 mb-1">{error}</p>
                    ))}
                    {session.errors.length > 3 && (
                      <p className="text-xs text-red-400 mt-1">
                        +{session.errors.length - 3} errores más
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
