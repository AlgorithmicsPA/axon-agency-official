"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useApiClient } from "@/lib/api";
import {
  ArrowLeft,
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Shield,
  Zap,
  Bug,
  FileCode,
  GitBranch,
  Clock,
  TrendingUp
} from "lucide-react";
import Link from "next/link";

interface Iteration {
  iteration_number: number;
  opportunity: any;
  proposal: any;
  council_decision: any;
  architect_decision: any;
  execution_result: any;
  success: boolean;
  timestamp: string;
}

interface Improvement {
  file_path: string;
  improvement_type: string;
  diff: string;
  council_review: any;
  architect_review: any;
  applied: boolean;
  outcome: any;
}

interface SessionDetail {
  session_id: string;
  status: string;
  mode: string;
  iteration: string;
  improvements_attempted: number;
  improvements_succeeded: number;
  improvements_failed: number;
  success_rate: number;
  started_at: string;
  errors: string[];
}

export default function SessionDetailPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const api = useApiClient();

  const [session, setSession] = useState<SessionDetail | null>(null);
  const [iterations, setIterations] = useState<Iteration[]>([]);
  const [improvements, setImprovements] = useState<Improvement[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"timeline" | "improvements">("timeline");
  const [selectedIteration, setSelectedIteration] = useState<number | null>(null);

  const loadData = async () => {
    try {
      const [sessionRes, iterationsRes, improvementsRes] = await Promise.all([
        api.get(`/api/agent/autonomous/sessions/${sessionId}`),
        api.get(`/api/agent/autonomous/sessions/${sessionId}/iterations`),
        api.get(`/api/agent/autonomous/sessions/${sessionId}/improvements`)
      ]);

      setSession(sessionRes.data);
      setIterations(iterationsRes.data);
      setImprovements(improvementsRes.data);
    } catch (error) {
      console.error("Error loading session:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, [sessionId]);

  const renderDiff = (diff: string) => {
    if (!diff) return null;

    const lines = diff.split("\n");
    return (
      <div className="bg-black/50 rounded-lg p-4 overflow-x-auto font-mono text-sm">
        {lines.map((line, idx) => {
          let className = "text-gray-300";
          if (line.startsWith("+")) className = "text-green-400 bg-green-500/10";
          if (line.startsWith("-")) className = "text-red-400 bg-red-500/10";
          if (line.startsWith("@@")) className = "text-cyan-400 bg-cyan-500/10";

          return (
            <div key={idx} className={`px-2 ${className}`}>
              {line || " "}
            </div>
          );
        })}
      </div>
    );
  };

  const renderCouncilDecision = (council: any) => {
    if (!council) return null;

    const getDecisionColor = (decision: string) => {
      if (decision === "approve") return "text-green-400 bg-green-500/20 border-green-500/50";
      if (decision === "revise") return "text-orange-400 bg-orange-500/20 border-orange-500/50";
      return "text-red-400 bg-red-500/20 border-red-500/50";
    };

    const getRiskColor = (risk: string) => {
      if (risk === "low") return "text-green-400";
      if (risk === "medium") return "text-orange-400";
      return "text-red-400";
    };

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold text-purple-400 flex items-center gap-2">
            👥 Decisión del Consejo de Revisión
          </h4>
          <span className={`px-3 py-1 rounded-lg border text-sm font-semibold ${getDecisionColor(council.decision)}`}>
            {council.decision.toUpperCase()}
          </span>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="bg-card border border-border rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="text-blue-400" size={18} />
              <span className="text-sm font-semibold">Security</span>
            </div>
            <p className={`text-xs ${getDecisionColor(council.security_decision)}`}>
              {council.security_decision}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Confianza: {(council.security_confidence * 100).toFixed(0)}%
            </p>
          </div>

          <div className="bg-card border border-border rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="text-yellow-400" size={18} />
              <span className="text-sm font-semibold">Performance</span>
            </div>
            <p className={`text-xs ${getDecisionColor(council.performance_decision)}`}>
              {council.performance_decision}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Confianza: {(council.performance_confidence * 100).toFixed(0)}%
            </p>
          </div>

          <div className="bg-card border border-border rounded-lg p-3">
            <div className="flex items-center gap-2 mb-2">
              <Bug className="text-red-400" size={18} />
              <span className="text-sm font-semibold">QA</span>
            </div>
            <p className={`text-xs ${getDecisionColor(council.qa_decision)}`}>
              {council.qa_decision}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Confianza: {(council.qa_confidence * 100).toFixed(0)}%
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">Riesgo General:</span>
          <span className={`font-semibold ${getRiskColor(council.overall_risk_level)}`}>
            {council.overall_risk_level.toUpperCase()}
          </span>
          <span className="text-sm text-muted-foreground">
            Confianza: {(council.overall_confidence * 100).toFixed(0)}%
          </span>
        </div>

        {council.concerns && council.concerns.length > 0 && (
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3">
            <p className="text-sm font-semibold text-orange-400 mb-2">⚠️ Preocupaciones:</p>
            <ul className="text-xs text-orange-300 space-y-1">
              {council.concerns.map((concern: string, idx: number) => (
                <li key={idx}>• {concern}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  const renderArchitectDecision = (architect: any) => {
    if (!architect) return null;

    const getDecisionColor = (decision: string) => {
      if (decision === "approve") return "text-green-400 bg-green-500/20 border-green-500/50";
      if (decision === "revise") return "text-orange-400 bg-orange-500/20 border-orange-500/50";
      return "text-red-400 bg-red-500/20 border-red-500/50";
    };

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-semibold text-cyan-400 flex items-center gap-2">
            🏛️ Decisión del Arquitecto Supervisor
          </h4>
          <span className={`px-3 py-1 rounded-lg border text-sm font-semibold ${getDecisionColor(architect.decision)}`}>
            {architect.decision.toUpperCase()}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">Confianza:</span>
          <span className="font-semibold text-cyan-400">
            {(architect.confidence * 100).toFixed(0)}%
          </span>
          <span className="text-sm text-muted-foreground">Riesgo:</span>
          <span className={`font-semibold ${architect.risk_level === "low" ? "text-green-400" : architect.risk_level === "medium" ? "text-orange-400" : "text-red-400"}`}>
            {architect.risk_level.toUpperCase()}
          </span>
        </div>

        {architect.reasoning && (
          <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-3">
            <p className="text-sm font-semibold text-cyan-400 mb-2">💭 Razonamiento:</p>
            <p className="text-sm text-cyan-200">{architect.reasoning}</p>
          </div>
        )}

        {architect.required_changes && architect.required_changes.length > 0 && (
          <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3">
            <p className="text-sm font-semibold text-orange-400 mb-2">🔧 Cambios Requeridos:</p>
            <ul className="text-xs text-orange-300 space-y-1">
              {architect.required_changes.map((change: string, idx: number) => (
                <li key={idx}>• {change}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Activity className="animate-spin text-cyan-400" size={48} />
      </div>
    );
  }

  if (!session) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Sesión no encontrada</p>
      </div>
    );
  }

  const selectedIterationData = selectedIteration !== null
    ? iterations.find(it => it.iteration_number === selectedIteration)
    : null;

  return (
    <div className="h-full flex flex-col space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/agent/autonomous"
          className="p-2 hover:bg-accent rounded-lg"
        >
          <ArrowLeft className="text-cyan-400" size={24} />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-cyan-400">
            Sesión: {session.session_id.slice(0, 12)}...
          </h1>
          <p className="text-muted-foreground mt-1">
            Modo: {session.mode} • {session.iteration}
          </p>
        </div>
        <div className={`px-4 py-2 rounded-lg font-semibold ${
          session.status === "running" ? "bg-green-500/20 text-green-400" :
          session.status === "completed" ? "bg-cyan-500/20 text-cyan-400" :
          "bg-gray-500/20 text-gray-400"
        }`}>
          {session.status.toUpperCase()}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="text-purple-400" size={20} />
            <span className="text-sm text-muted-foreground">Intentadas</span>
          </div>
          <p className="text-2xl font-bold">{session.improvements_attempted}</p>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="text-green-400" size={20} />
            <span className="text-sm text-muted-foreground">Exitosas</span>
          </div>
          <p className="text-2xl font-bold text-green-400">{session.improvements_succeeded}</p>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <XCircle className="text-red-400" size={20} />
            <span className="text-sm text-muted-foreground">Fallidas</span>
          </div>
          <p className="text-2xl font-bold text-red-400">{session.improvements_failed}</p>
        </div>

        <div className="bg-card border border-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="text-cyan-400" size={20} />
            <span className="text-sm text-muted-foreground">Tasa Éxito</span>
          </div>
          <p className="text-2xl font-bold text-cyan-400">
            {(session.success_rate * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="flex gap-2 border-b border-border">
        <button
          onClick={() => setActiveTab("timeline")}
          className={`px-6 py-3 font-semibold transition-colors ${
            activeTab === "timeline"
              ? "text-cyan-400 border-b-2 border-cyan-400"
              : "text-muted-foreground hover:text-foreground"
          }`}
        >
          📊 Timeline de Iteraciones
        </button>
        <button
          onClick={() => setActiveTab("improvements")}
          className={`px-6 py-3 font-semibold transition-colors ${
            activeTab === "improvements"
              ? "text-cyan-400 border-b-2 border-cyan-400"
              : "text-muted-foreground hover:text-foreground"
          }`}>
          🔧 Mejoras Detalladas
        </button>
      </div>

      <div className="flex-1 overflow-auto">
        {activeTab === "timeline" && (
          <div className="space-y-4">
            {iterations.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                No hay iteraciones todavía
              </div>
            ) : (
              iterations.map((iter) => (
                <div
                  key={iter.iteration_number}
                  className={`bg-card border rounded-lg p-6 cursor-pointer transition-colors ${
                    selectedIteration === iter.iteration_number
                      ? "border-cyan-500"
                      : "border-border hover:border-cyan-500/50"
                  }`}
                  onClick={() => setSelectedIteration(
                    selectedIteration === iter.iteration_number ? null : iter.iteration_number
                  )}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-lg font-bold text-cyan-400">
                          Iteración #{iter.iteration_number}
                        </span>
                        {iter.success ? (
                          <CheckCircle className="text-green-400" size={20} />
                        ) : (
                          <XCircle className="text-red-400" size={20} />
                        )}
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock size={14} />
                        {new Date(iter.timestamp).toLocaleString('es-ES')}
                      </div>
                    </div>
                  </div>

                  {iter.opportunity && (
                    <div className="mb-4">
                      <p className="text-sm font-semibold text-purple-400 mb-2">
                        🎯 Oportunidad Detectada:
                      </p>
                      <p className="text-sm">
                        {iter.opportunity.file_path} - {iter.opportunity.improvement_type}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {iter.opportunity.description}
                      </p>
                    </div>
                  )}

                  {selectedIteration === iter.iteration_number && (
                    <div className="space-y-6 mt-6 pt-6 border-t border-border">
                      {iter.council_decision && renderCouncilDecision(iter.council_decision)}
                      {iter.architect_decision && (
                        <div className="mt-6">
                          {renderArchitectDecision(iter.architect_decision)}
                        </div>
                      )}

                      {iter.execution_result && (
                        <div>
                          <h4 className="font-semibold text-green-400 mb-2">
                            ✅ Resultado de Ejecución
                          </h4>
                          <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                            <p className="text-sm">{iter.execution_result.message || "Completado"}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "improvements" && (
          <div className="space-y-6">
            {improvements.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                No hay mejoras aplicadas todavía
              </div>
            ) : (
              improvements.map((imp, idx) => (
                <div key={idx} className="bg-card border border-border rounded-lg p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <FileCode className="text-cyan-400" size={20} />
                        <span className="font-mono text-sm text-cyan-400">
                          {imp.file_path}
                        </span>
                        {imp.applied ? (
                          <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                            APLICADO
                          </span>
                        ) : (
                          <span className="px-2 py-1 bg-red-500/20 text-red-400 text-xs rounded">
                            NO APLICADO
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Tipo: {imp.improvement_type} • Resultado: {typeof imp.outcome === 'string' ? imp.outcome : imp.outcome?.success ? 'Exitoso' : 'Fallido'}
                      </p>
                    </div>
                  </div>

                  {imp.diff && (
                    <div className="mb-4">
                      <p className="text-sm font-semibold mb-2 flex items-center gap-2">
                        <GitBranch size={16} />
                        Cambios en el Código:
                      </p>
                      {renderDiff(imp.diff)}
                    </div>
                  )}

                  {imp.council_review && (
                    <div className="mb-4">
                      {renderCouncilDecision(imp.council_review)}
                    </div>
                  )}

                  {imp.architect_review && renderArchitectDecision(imp.architect_review)}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
