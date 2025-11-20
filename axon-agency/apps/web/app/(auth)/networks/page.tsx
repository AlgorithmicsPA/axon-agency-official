"use client";

import { useEffect, useState } from "react";
import { useApiClient } from "@/lib/api";
import { Network, Server, Zap, CheckCircle, XCircle } from "lucide-react";

export default function NetworksPage() {
  const api = useApiClient();
  const [axonCoreStatus, setAxonCoreStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await api.get("/api/axon-core/health");
      setAxonCoreStatus(res.data);
    } catch (error) {
      console.error("Error fetching Axon Core status:", error);
      setAxonCoreStatus({ status: "disconnected" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-cyan-400">Redes Conectadas</h1>
        <p className="text-muted-foreground">Integraciones y servicios externos</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className={`bg-card p-6 rounded-lg border ${
          axonCoreStatus?.status === 'connected' 
            ? 'border-green-500/20' 
            : 'border-red-500/20'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Server className="text-cyan-400" size={24} />
              <div>
                <h3 className="font-bold">Axon Core</h3>
                <p className="text-sm text-muted-foreground">Sistema de infraestructura</p>
              </div>
            </div>
            {!loading && (
              axonCoreStatus?.status === 'connected' ? (
                <CheckCircle className="text-green-400" size={24} />
              ) : (
                <XCircle className="text-red-400" size={24} />
              )
            )}
          </div>
          
          {!loading && axonCoreStatus?.status === 'connected' && (
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Estado:</span>
                <span className="text-green-400 font-medium">Conectado</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Endpoint:</span>
                <span className="text-cyan-400 text-xs">{axonCoreStatus.remote}</span>
              </div>
            </div>
          )}

          {!loading && axonCoreStatus?.status === 'disconnected' && (
            <div className="text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Estado:</span>
                <span className="text-red-400 font-medium">Desconectado</span>
              </div>
            </div>
          )}
        </div>

        <div className="bg-card p-6 rounded-lg border border-border opacity-50">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Zap className="text-yellow-400" size={24} />
              <div>
                <h3 className="font-bold">n8n Workflows</h3>
                <p className="text-sm text-muted-foreground">Automatizaciones</p>
              </div>
            </div>
            <div className="text-sm text-muted-foreground">Próximamente</div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border opacity-50">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Network className="text-purple-400" size={24} />
              <div>
                <h3 className="font-bold">Cloudflare Tunnel</h3>
                <p className="text-sm text-muted-foreground">Túnel seguro</p>
              </div>
            </div>
            <div className="text-sm text-muted-foreground">Próximamente</div>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border opacity-50">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Server className="text-green-400" size={24} />
              <div>
                <h3 className="font-bold">Redis Queue</h3>
                <p className="text-sm text-muted-foreground">Cola de trabajos</p>
              </div>
            </div>
            <div className="text-sm text-muted-foreground">Próximamente</div>
          </div>
        </div>
      </div>

      <div className="bg-card p-6 rounded-lg border border-border">
        <h2 className="text-lg font-bold mb-4">Sobre las Redes Conectadas</h2>
        <p className="text-muted-foreground text-sm mb-4">
          AXON Agency se integra con múltiples servicios externos para proporcionar funcionalidades avanzadas:
        </p>
        <ul className="space-y-2 text-sm text-muted-foreground">
          <li className="flex items-start gap-2">
            <span className="text-cyan-400">•</span>
            <span><strong>Axon Core:</strong> Sistema centralizado de infraestructura para servicios, comandos y LLMs</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-yellow-400">•</span>
            <span><strong>n8n:</strong> Motor de workflows para automatizaciones complejas</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-400">•</span>
            <span><strong>Cloudflare Tunnel:</strong> Conexión segura entre servicios sin exponer puertos</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-green-400">•</span>
            <span><strong>Redis:</strong> Cola de trabajos para procesamiento asíncrono y cache</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
