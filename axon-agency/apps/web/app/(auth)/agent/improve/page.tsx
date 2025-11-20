"use client";

import { useState, useEffect } from "react";
import { useApiClient } from "@/lib/api";
import {
  CheckCircle,
  XCircle,
  Clock,
  Sparkles,
  GitBranch,
  Play,
  Trash2,
  Eye,
  AlertCircle,
  TrendingUp,
  Code,
  FileText,
} from "lucide-react";
import { useToast } from "@/components/Toast";
import { useConfirm } from "@/components/ConfirmModal";

type ImprovementType =
  | "refactor"
  | "performance"
  | "security"
  | "testing"
  | "documentation"
  | "bug_fix"
  | "feature"
  | "dependency_update";

type JobStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "running"
  | "completed"
  | "failed"
  | "cancelled"
  | "applied";

interface ImprovementJob {
  job_id: string;
  improvement_type: ImprovementType;
  target_file: string;
  description: string;
  rationale: string;
  success_criteria: string[];
  status: JobStatus;
  metrics?: {
    before_loc?: number;
    after_loc?: number;
    complexity_before?: number;
    complexity_after?: number;
  };
  diff_preview?: string;
  created_at: string;
  updated_at: string;
}

interface ArchNode {
  name: string;
  path: string;
  type: string;
  loc: number;
  complexity: number;
  imports: string[];
  exports: string[];
}

interface ArchEdge {
  source: string;
  target: string;
  import_type: string;
}

interface ArchData {
  nodes: ArchNode[];
  edges: ArchEdge[];
  total_files: number;
  total_loc: number;
  avg_complexity: number;
}

export default function ImprovePage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const { confirm } = useConfirm();
  const [jobs, setJobs] = useState<ImprovementJob[]>([]);
  const [archData, setArchData] = useState<ArchData | null>(null);
  const [selectedJob, setSelectedJob] = useState<ImprovementJob | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadJobs();
    loadArchitecture();
  }, []);

  const loadJobs = async () => {
    try {
      const res = await api.get("/api/improve/jobs");
      setJobs(res.data.jobs || []);
    } catch (error: any) {
      if (error?.response?.status === 403 || error?.response?.status === 401) {
        console.log("Autenticación requerida - jobs list vacía");
        setJobs([]);
      } else {
        console.error("Error loading jobs:", error);
      }
    }
  };

  const loadArchitecture = async () => {
    setAnalyzing(true);
    try {
      console.log("Loading architecture from /api/self-improve/structure...");
      const res = await api.get("/api/self-improve/structure");
      console.log("Architecture response:", res.data);
      
      const files = res.data.files || {};
      const depGraph = res.data.dependency_graph || {};
      
      const nodes = Object.entries(files).map(([path, data]: [string, any]) => ({
        name: path.split('/').pop() || path,
        path,
        type: path.endsWith('.py') ? 'python' : 'typescript',
        loc: data.loc || 0,
        complexity: data.complexity || 0,
        imports: data.imports || [],
        exports: data.classes?.concat(data.functions || []) || [],
      }));
      
      const edges = Object.entries(depGraph).flatMap(([source, targets]: [string, any]) =>
        (targets || []).map((target: string) => ({
          source,
          target,
          import_type: 'import',
        }))
      );
      
      const totalComplexity = nodes.reduce((sum, n) => sum + n.complexity, 0);
      const avgComplexity = nodes.length > 0 ? totalComplexity / nodes.length : 0;
      
      const archDataObj = {
        nodes,
        edges,
        total_files: res.data.stats?.total_files || nodes.length,
        total_loc: res.data.stats?.total_loc || nodes.reduce((sum, n) => sum + n.loc, 0),
        avg_complexity: avgComplexity,
      };
      
      console.log("Architecture data:", archDataObj);
      setArchData(archDataObj);
    } catch (error: any) {
      console.error("Error loading architecture:", error);
      console.error("Error details:", error?.response?.data);
    } finally {
      console.log("Setting analyzing to false");
      setAnalyzing(false);
    }
  };

  const analyzeAndSuggest = async () => {
    setAnalyzing(true);
    try {
      const res = await api.post("/api/improve/jobs/analyze");
      await loadJobs();
      showToast(`✅ Análisis completo. ${res.data.jobs_created || 0} mejoras sugeridas.`, "success");
    } catch (error: any) {
      console.error("Error analyzing:", error);
      if (error?.response?.status === 403 || error?.response?.status === 401) {
        showToast("⚠️ Autenticación requerida para crear trabajos de mejora", "info");
      } else {
        showToast(`❌ Error al analizar: ${error?.response?.data?.detail || "Error desconocido"}`, "error");
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const approveJob = async (jobId: string) => {
    try {
      await api.post(`/api/improve/jobs/${jobId}/approve`);
      await loadJobs();
    } catch (error) {
      console.error("Error approving job:", error);
    }
  };

  const executeJob = async (jobId: string) => {
    setLoading(true);
    try {
      await api.post(`/api/improve/jobs/${jobId}/execute`);
      showToast("✅ Mejora ejecutándose en segundo plano", "success");
      setTimeout(loadJobs, 2000);
    } catch (error) {
      console.error("Error executing job:", error);
      showToast("❌ Error al ejecutar mejora", "error");
    } finally {
      setLoading(false);
    }
  };

  const applyJob = async (jobId: string) => {
    const confirmed = await confirm({
      title: "Confirmar aplicar mejora",
      message: "¿Aplicar esta mejora al código principal?",
      variant: "warning"
    });
    if (!confirmed) return;
    setLoading(true);
    try {
      await api.post(`/api/improve/jobs/${jobId}/apply`);
      showToast("✅ Mejora aplicada exitosamente", "success");
      await loadJobs();
    } catch (error) {
      console.error("Error applying job:", error);
      showToast("❌ Error al aplicar mejora", "error");
    } finally {
      setLoading(false);
    }
  };

  const cleanupJob = async (jobId: string) => {
    try {
      await api.delete(`/api/improve/jobs/${jobId}/cleanup`);
      await loadJobs();
    } catch (error) {
      console.error("Error cleaning up job:", error);
    }
  };

  const getStatusIcon = (status: JobStatus) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="text-green-500" size={20} />;
      case "failed":
        return <XCircle className="text-red-500" size={20} />;
      case "running":
        return <Clock className="text-yellow-500 animate-spin" size={20} />;
      case "approved":
        return <Play className="text-cyan-500" size={20} />;
      case "applied":
        return <CheckCircle className="text-emerald-500" size={20} />;
      default:
        return <AlertCircle className="text-gray-500" size={20} />;
    }
  };

  const getTypeColor = (type: ImprovementType) => {
    const colors = {
      refactor: "bg-purple-500/20 text-purple-300",
      performance: "bg-orange-500/20 text-orange-300",
      security: "bg-red-500/20 text-red-300",
      testing: "bg-blue-500/20 text-blue-300",
      documentation: "bg-green-500/20 text-green-300",
      bug_fix: "bg-yellow-500/20 text-yellow-300",
      feature: "bg-cyan-500/20 text-cyan-300",
      dependency_update: "bg-pink-500/20 text-pink-300",
    };
    return colors[type] || "bg-gray-500/20 text-gray-300";
  };

  return (
    <div className="h-full flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400 flex items-center gap-3">
            <Sparkles size={32} />
            Mejoras Autónomas
          </h1>
          <p className="text-muted-foreground mt-1">
            El agente analiza y mejora su propio código automáticamente
          </p>
        </div>
        <button
          onClick={analyzeAndSuggest}
          disabled={analyzing}
          className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 rounded-lg flex items-center gap-2 font-semibold"
        >
          <TrendingUp size={20} />
          {analyzing ? "Analizando..." : "Analizar y Sugerir"}
        </button>
      </div>

      {/* Architecture Overview */}
      {archData ? (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <FileText size={20} className="text-cyan-400" />
              <span className="text-sm text-muted-foreground">Archivos</span>
            </div>
            <div className="text-2xl font-bold">{archData.total_files}</div>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Code size={20} className="text-purple-400" />
              <span className="text-sm text-muted-foreground">Líneas de Código</span>
            </div>
            <div className="text-2xl font-bold">{archData.total_loc.toLocaleString()}</div>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <GitBranch size={20} className="text-orange-400" />
              <span className="text-sm text-muted-foreground">Dependencias</span>
            </div>
            <div className="text-2xl font-bold">{archData.edges.length}</div>
          </div>
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp size={20} className="text-green-400" />
              <span className="text-sm text-muted-foreground">Complejidad Promedio</span>
            </div>
            <div className="text-2xl font-bold">{archData.avg_complexity.toFixed(1)}</div>
          </div>
        </div>
      ) : (
        <div className="bg-card border border-border rounded-lg p-4 text-center text-muted-foreground">
          <TrendingUp size={32} className="mx-auto mb-2 opacity-50" />
          <p>Cargando estadísticas de arquitectura...</p>
        </div>
      )}

      {/* Jobs List */}
      <div className="flex-1 grid grid-cols-2 gap-6 overflow-hidden">
        <div className="flex flex-col gap-4 overflow-y-auto">
          <h2 className="text-xl font-semibold">Trabajos de Mejora ({jobs.length})</h2>
          {jobs.length === 0 ? (
            <div className="bg-card border border-border rounded-lg p-8 text-center text-muted-foreground">
              <Sparkles size={48} className="mx-auto mb-4 opacity-50" />
              <p>No hay mejoras pendientes</p>
              <p className="text-sm mt-2">Haz clic en "Analizar y Sugerir" para empezar</p>
            </div>
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => (
                <div
                  key={job.job_id}
                  onClick={() => setSelectedJob(job)}
                  className={`bg-card border rounded-lg p-4 cursor-pointer transition-all ${
                    selectedJob?.job_id === job.job_id
                      ? "border-cyan-500 shadow-lg shadow-cyan-500/20"
                      : "border-border hover:border-cyan-500/50"
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(job.status)}
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${getTypeColor(job.improvement_type)}`}>
                        {job.improvement_type}
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {new Date(job.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="font-semibold mb-1">{job.description}</h3>
                  <p className="text-sm text-muted-foreground mb-2">{job.target_file}</p>
                  <p className="text-xs text-muted-foreground line-clamp-2">{job.rationale}</p>

                  {job.metrics && (
                    <div className="flex gap-4 mt-3 pt-3 border-t border-border text-xs">
                      {job.metrics.before_loc && job.metrics.after_loc && (
                        <div>
                          LOC: {job.metrics.before_loc} → {job.metrics.after_loc}
                          <span
                            className={
                              job.metrics.after_loc < job.metrics.before_loc ? "text-green-400 ml-1" : "text-red-400 ml-1"
                            }
                          >
                            ({job.metrics.after_loc - job.metrics.before_loc > 0 ? "+" : ""}
                            {job.metrics.after_loc - job.metrics.before_loc})
                          </span>
                        </div>
                      )}
                      {job.metrics.complexity_before && job.metrics.complexity_after && (
                        <div>
                          Complejidad: {job.metrics.complexity_before.toFixed(1)} →{" "}
                          {job.metrics.complexity_after.toFixed(1)}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Job Detail & Diff Preview */}
        <div className="flex flex-col gap-4 overflow-hidden">
          {selectedJob ? (
            <>
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold">Detalles de Mejora</h2>
                <div className="flex gap-2">
                  {selectedJob.status === "pending" && (
                    <button
                      onClick={() => approveJob(selectedJob.job_id)}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm"
                    >
                      Aprobar
                    </button>
                  )}
                  {selectedJob.status === "approved" && (
                    <button
                      onClick={() => executeJob(selectedJob.job_id)}
                      disabled={loading}
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 rounded-lg text-sm flex items-center gap-2"
                    >
                      <Play size={16} />
                      Ejecutar
                    </button>
                  )}
                  {selectedJob.status === "completed" && (
                    <>
                      <button
                        onClick={() => applyJob(selectedJob.job_id)}
                        disabled={loading}
                        className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 rounded-lg text-sm flex items-center gap-2"
                      >
                        <CheckCircle size={16} />
                        Aplicar
                      </button>
                      <button
                        onClick={() => cleanupJob(selectedJob.job_id)}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm flex items-center gap-2"
                      >
                        <Trash2 size={16} />
                        Limpiar
                      </button>
                    </>
                  )}
                </div>
              </div>

              <div className="bg-card border border-border rounded-lg p-4">
                <h3 className="font-semibold mb-2">{selectedJob.description}</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Archivo:</span>
                    <code className="ml-2 bg-accent px-2 py-1 rounded">{selectedJob.target_file}</code>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Tipo:</span>
                    <span className={`ml-2 px-2 py-1 rounded ${getTypeColor(selectedJob.improvement_type)}`}>
                      {selectedJob.improvement_type}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Estado:</span>
                    <span className="ml-2 font-semibold">{selectedJob.status}</span>
                  </div>
                </div>

                <div className="mt-4">
                  <h4 className="font-semibold mb-2">Justificación:</h4>
                  <p className="text-sm text-muted-foreground">{selectedJob.rationale}</p>
                </div>

                <div className="mt-4">
                  <h4 className="font-semibold mb-2">Criterios de Éxito:</h4>
                  <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                    {selectedJob.success_criteria.map((criterion, idx) => (
                      <li key={idx}>{criterion}</li>
                    ))}
                  </ul>
                </div>
              </div>

              {selectedJob.diff_preview && (
                <div className="flex-1 flex flex-col overflow-hidden">
                  <h3 className="font-semibold mb-2 flex items-center gap-2">
                    <Eye size={18} />
                    Vista Previa de Cambios
                  </h3>
                  <pre className="flex-1 bg-black/50 border border-border rounded-lg p-4 text-xs overflow-auto font-mono">
                    {selectedJob.diff_preview}
                  </pre>
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <Eye size={48} className="mx-auto mb-4 opacity-50" />
                <p>Selecciona un trabajo para ver los detalles</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
