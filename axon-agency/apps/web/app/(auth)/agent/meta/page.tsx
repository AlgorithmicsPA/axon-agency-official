"use client";

import { useState, useEffect } from "react";
import { useApiClient } from "@/lib/api";
import { ToastProvider, useToast } from "@/components/Toast";
import { ConfirmProvider, useConfirm } from "@/components/ConfirmModal";
import {
  Users,
  Shield,
  Zap,
  Bug,
  Wrench,
  Brain,
  Microscope,
  Plus,
  Copy,
  TrendingUp,
  Activity,
  CheckCircle,
  XCircle
} from "lucide-react";

interface SpecializedAgent {
  agent_id: string;
  name: string;
  role: string;
  tenant_id: string;
  status: string;
  tasks_completed: number;
  success_rate: number;
  created_at: string;
  last_active: string;
}

interface UsageStats {
  total_agents: number;
  active_agents: number;
  total_tasks: number;
  overall_success_rate: number;
}

const ROLE_ICONS: Record<string, any> = {
  SECURITY: Shield,
  PERFORMANCE: Zap,
  QA: Bug,
  BUILDER: Wrench,
  PLANNER: Brain,
  TESTER: Microscope
};

const ROLE_COLORS: Record<string, string> = {
  SECURITY: "bg-blue-500/20 text-blue-400 border-blue-500/50",
  PERFORMANCE: "bg-yellow-500/20 text-yellow-400 border-yellow-500/50",
  QA: "bg-red-500/20 text-red-400 border-red-500/50",
  BUILDER: "bg-purple-500/20 text-purple-400 border-purple-500/50",
  PLANNER: "bg-cyan-500/20 text-cyan-400 border-cyan-500/50",
  TESTER: "bg-green-500/20 text-green-400 border-green-500/50"
};

function MetaAgentContent() {
  const api = useApiClient();
  const { showToast } = useToast();
  const { confirm } = useConfirm();
  const [agents, setAgents] = useState<SpecializedAgent[]>([]);
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [creatingAgent, setCreatingAgent] = useState(false);
  const [replicatingAgent, setReplicatingAgent] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAgentName, setNewAgentName] = useState("");
  const [newAgentRole, setNewAgentRole] = useState("SECURITY");
  const [tenantId] = useState("tenant_default");

  const loadData = async () => {
    try {
      const [agentsRes, usageRes] = await Promise.all([
        api.get("/api/agent/meta/agents"),
        api.get(`/api/agent/meta/governance/usage/${tenantId}`)
      ]);
      setAgents(agentsRes.data);
      setUsage(usageRes.data);
    } catch (error) {
      console.error("Error loading data:", error);
      showToast("Error al cargar datos", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const createAgent = async () => {
    if (!newAgentName.trim()) {
      showToast("Por favor ingresa un nombre para el agente", "error");
      return;
    }

    setCreatingAgent(true);
    try {
      await api.post("/api/agent/meta/create", {
        name: newAgentName,
        role: newAgentRole.toLowerCase(),
        tenant_id: tenantId
      });
      setNewAgentName("");
      setShowCreateModal(false);
      showToast("Agente creado exitosamente", "success");
      await loadData();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail;
      if (typeof errorMsg === 'string') {
        showToast(errorMsg, "error");
      } else if (Array.isArray(errorMsg)) {
        showToast(errorMsg.map((e: any) => e.msg).join(', '), "error");
      } else {
        showToast("Error al crear agente", "error");
      }
    } finally {
      setCreatingAgent(false);
    }
  };

  const deleteAgent = async (agentId: string) => {
    const confirmed = await confirm({
      title: "Eliminar Agente",
      message: "¿Estás seguro de que deseas eliminar este agente especializado? Esta acción no se puede deshacer.",
      confirmText: "Eliminar",
      cancelText: "Cancelar",
      variant: "danger"
    });

    if (!confirmed) return;

    try {
      await api.del(`/api/agent/meta/agents/${agentId}`);
      showToast("Agente eliminado exitosamente", "success");
      await loadData();
    } catch (error: any) {
      showToast(error.response?.data?.detail || "Error al eliminar agente", "error");
    }
  };

  const replicateAgent = async (agentId: string, agentName: string) => {
    const confirmed = await confirm({
      title: "Replicar Agente",
      message: `¿Deseas replicar "${agentName}"? Se creará una copia del agente con su configuración y capacidades.`,
      confirmText: "Replicar",
      cancelText: "Cancelar",
      variant: "info"
    });

    if (!confirmed) return;

    setReplicatingAgent(agentId);
    try {
      await api.post("/api/agent/meta/replicate", {
        source_agent_id: agentId,
        target_tenant_id: tenantId,
        inherit_training: true
      });
      showToast("Agente replicado exitosamente", "success");
      await loadData();
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail;
      showToast(errorMsg || "Error al replicar agente", "error");
    } finally {
      setReplicatingAgent(null);
    }
  };

  const getRoleIcon = (role: string) => {
    const Icon = ROLE_ICONS[role] || Users;
    return <Icon size={20} />;
  };

  const getRoleColor = (role: string) => {
    return ROLE_COLORS[role] || "bg-gray-500/20 text-gray-400 border-gray-500/50";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Activity className="animate-spin text-cyan-400" size={48} />
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Meta-Agente</h1>
          <p className="text-muted-foreground mt-1">Sistema de Agentes Especializados Multi-Tenant</p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 rounded-lg flex items-center gap-2 font-semibold"
        >
          <Plus size={20} />
          Crear Agente
        </button>
      </div>

      {usage && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Agentes</p>
                <p className="text-2xl font-bold text-cyan-400">{usage.total_agents}</p>
              </div>
              <Users className="text-cyan-500/50" size={32} />
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Agentes Activos</p>
                <p className="text-2xl font-bold text-green-400">{usage.active_agents}</p>
              </div>
              <Activity className="text-green-500/50" size={32} />
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Tareas Completadas</p>
                <p className="text-2xl font-bold text-purple-400">{usage.total_tasks}</p>
              </div>
              <CheckCircle className="text-purple-500/50" size={32} />
            </div>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Tasa de Éxito</p>
                <p className="text-2xl font-bold text-orange-400">
                  {(usage.overall_success_rate * 100).toFixed(1)}%
                </p>
              </div>
              <TrendingUp className="text-orange-500/50" size={32} />
            </div>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">Crear Agente Especializado</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-muted-foreground mb-2">Nombre del Agente</label>
                <input
                  type="text"
                  value={newAgentName}
                  onChange={(e) => setNewAgentName(e.target.value)}
                  placeholder="ej: Security Agent Alpha"
                  className="w-full px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm text-muted-foreground mb-2">Rol Especializado</label>
                <select
                  value={newAgentRole}
                  onChange={(e) => setNewAgentRole(e.target.value)}
                  className="w-full px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                >
                  <option value="SECURITY">🛡️ Security - Seguridad y Vulnerabilidades</option>
                  <option value="PERFORMANCE">⚡ Performance - Optimización y Rendimiento</option>
                  <option value="QA">🐛 QA - Control de Calidad y Testing</option>
                  <option value="BUILDER">🔧 Builder - Construcción y Arquitectura</option>
                  <option value="PLANNER">🧠 Planner - Planificación y Diseño</option>
                  <option value="TESTER">🔬 Tester - Testing Automatizado</option>
                </select>
              </div>

              <div className="flex gap-2 pt-4">
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg"
                >
                  Cancelar
                </button>
                <button
                  onClick={createAgent}
                  disabled={creatingAgent}
                  className="flex-1 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:bg-cyan-700 disabled:opacity-50 rounded-lg font-semibold"
                >
                  {creatingAgent ? "Creando..." : "Crear Agente"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-auto">
        <h2 className="text-xl font-semibold mb-4">Agentes Especializados</h2>

        {agents.length === 0 ? (
          <div className="bg-card border border-border rounded-lg p-12 text-center">
            <Users className="mx-auto text-muted-foreground mb-4" size={64} />
            <p className="text-muted-foreground">No hay agentes especializados todavía</p>
            <p className="text-sm text-muted-foreground mt-2">Crea tu primer agente para comenzar</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <div
                key={agent.agent_id}
                className="bg-card border border-border rounded-lg p-6 hover:border-cyan-500/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className={`p-3 rounded-lg border ${getRoleColor(agent.role)}`}>
                      {getRoleIcon(agent.role)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-cyan-400">{agent.name}</h3>
                      <p className="text-xs text-muted-foreground">{agent.agent_id.slice(0, 12)}...</p>
                    </div>
                  </div>

                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    agent.status === "ACTIVE" ? "bg-green-500/20 text-green-400" :
                    agent.status === "BUSY" ? "bg-orange-500/20 text-orange-400" :
                    "bg-gray-500/20 text-gray-400"
                  }`}>
                    {agent.status}
                  </span>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Tareas Completadas:</span>
                    <span className="font-semibold">{agent.tasks_completed}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Tasa de Éxito:</span>
                    <span className="font-semibold text-green-400">
                      {(agent.success_rate * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Última Actividad:</span>
                    <span className="text-xs">
                      {new Date(agent.last_active).toLocaleDateString('es-ES')}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={() => replicateAgent(agent.agent_id, agent.name)}
                    disabled={replicatingAgent === agent.agent_id}
                    className="flex-1 px-3 py-2 bg-purple-500/20 hover:bg-purple-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-purple-400 rounded-lg text-sm flex items-center justify-center gap-2"
                  >
                    <Copy size={14} className={replicatingAgent === agent.agent_id ? "animate-spin" : ""} />
                    {replicatingAgent === agent.agent_id ? "Replicando..." : "Replicar"}
                  </button>
                  <button
                    onClick={() => deleteAgent(agent.agent_id)}
                    className="px-3 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg text-sm"
                  >
                    <XCircle size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function MetaAgentPage() {
  return (
    <ToastProvider>
      <ConfirmProvider>
        <MetaAgentContent />
      </ConfirmProvider>
    </ToastProvider>
  );
}
