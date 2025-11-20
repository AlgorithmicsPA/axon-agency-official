"use client";

import { useEffect, useState } from "react";
import { useApiClient } from "@/lib/api";
import { Bot, Play, Zap, Clock, CheckCircle } from "lucide-react";
import { useToast } from "@/components/Toast";

export default function AutopilotsPage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const [autopilots, setAutopilots] = useState<any[]>([]);
  const [executing, setExecuting] = useState<{[key: number]: boolean}>({});

  useEffect(() => {
    fetchAutopilots();
  }, []);

  const fetchAutopilots = async () => {
    try {
      const res = await api.get("/api/autopilots/list");
      setAutopilots(res.data.items || []);
    } catch (error) {
      console.error("Error fetching autopilots:", error);
    }
  };

  const triggerAutopilot = async (id: number) => {
    setExecuting({...executing, [id]: true});
    try {
      await api.post(`/api/autopilots/${id}/trigger`, {});
      showToast("Autopilot ejecutado exitosamente", "success");
    } catch (error) {
      console.error("Error triggering autopilot:", error);
      showToast("Error al ejecutar autopilot", "error");
    } finally {
      setExecuting({...executing, [id]: false});
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Autopilotos IA</h1>
          <p className="text-muted-foreground">Automatizaciones inteligentes para tu agencia</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Bot className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Total Autopilotos</p>
          </div>
          <p className="text-3xl font-bold">{autopilots.length}</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Zap className="text-yellow-400" size={20} />
            <p className="text-sm font-medium">Activos</p>
          </div>
          <p className="text-3xl font-bold">
            {autopilots.filter(a => a.enabled).length}
          </p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="text-green-400" size={20} />
            <p className="text-sm font-medium">Ejecuciones Hoy</p>
          </div>
          <p className="text-3xl font-bold">24</p>
        </div>
      </div>

      <div className="grid gap-4">
        {autopilots.map((autopilot) => (
          <div
            key={autopilot.id}
            className="bg-card p-6 rounded-lg border border-border hover:border-cyan-500/40 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <Bot className="text-cyan-400" size={24} />
                  <h3 className="text-xl font-bold">{autopilot.name}</h3>
                </div>
                <p className="text-muted-foreground mb-4">{autopilot.description}</p>
                <div className="flex items-center gap-4">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      autopilot.enabled
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-gray-500/20 text-gray-400'
                    }`}
                  >
                    {autopilot.enabled ? 'Activo' : 'Inactivo'}
                  </span>
                  <span className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock size={14} />
                    Última ejecución: {new Date(autopilot.last_run || Date.now()).toLocaleString()}
                  </span>
                </div>
              </div>
              <button
                onClick={() => triggerAutopilot(autopilot.id)}
                disabled={executing[autopilot.id] || !autopilot.enabled}
                className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
              >
                <Play size={16} />
                {executing[autopilot.id] ? 'Ejecutando...' : 'Ejecutar'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {autopilots.length === 0 && (
        <div className="bg-card p-12 rounded-lg border border-border text-center">
          <Bot className="mx-auto mb-4 text-muted-foreground" size={48} />
          <p className="text-muted-foreground">No hay autopilotos configurados</p>
        </div>
      )}
    </div>
  );
}
