"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { AgentForm } from "@/components/catalog/AgentForm";
import { ReplitStudioPlaceholder } from "@/components/catalog/ReplitStudioPlaceholder";
import { AdminOnly, AuthenticatedOnly } from "@/components/auth/RoleGuard";
import { 
  Megaphone, Code, Phone, Layout, CheckCircle, FileText,
  ArrowLeft, LucideIcon 
} from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";

interface AgentDetail {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  capabilities: string[];
  pricing: string;
}

const iconMap: Record<string, LucideIcon> = {
  megaphone: Megaphone,
  code: Code,
  phone: Phone,
  layout: Layout,
  "check-circle": CheckCircle,
  "file-text": FileText,
};

export default function AgentDetailPage() {
  const params = useParams();
  const agentId = params.id as string;

  const [agent, setAgent] = useState<AgentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAgentDetail();
  }, [agentId]);

  const fetchAgentDetail = async () => {
    try {
      const response = await fetch(`/api/catalog/agents/${agentId}`);
      
      if (!response.ok) {
        throw new Error("Agente no encontrado");
      }

      const data = await response.json();
      setAgent(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="h-12 w-48 bg-card animate-pulse rounded" />
        <div className="h-96 bg-card animate-pulse rounded" />
      </div>
    );
  }

  if (error || !agent) {
    return (
      <div className="space-y-6">
        <Link
          href="/catalog"
          className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Volver al catálogo
        </Link>
        <div className="p-8 bg-card border border-border rounded-lg text-center">
          <p className="text-red-400">
            {error || "No se pudo cargar el agente"}
          </p>
        </div>
      </div>
    );
  }

  const Icon = iconMap[agent.icon] || Code;

  return (
    <div className="space-y-6">
      <Link
        href="/catalog"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Volver al catálogo
      </Link>

      <div className="bg-card border border-border rounded-lg p-8">
        <div className="flex items-start gap-6 mb-6">
          <div className="p-4 bg-cyan-500/10 rounded-lg">
            <Icon className="h-10 w-10 text-cyan-400" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{agent.name}</h1>
              <Badge variant="outline">{agent.category}</Badge>
            </div>
            <p className="text-muted-foreground mb-4">{agent.description}</p>
            <p className="text-cyan-400 font-medium">{agent.pricing}</p>
          </div>
        </div>

        <div className="border-t border-border pt-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Capacidades</h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {agent.capabilities.map((capability, index) => (
              <li key={index} className="flex items-start gap-2">
                <CheckCircle className="h-5 w-5 text-cyan-400 mt-0.5 shrink-0" />
                <span className="text-sm">{capability}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-lg p-8">
          <h2 className="text-xl font-semibold mb-4">Solicitar Agente</h2>
          
          <AuthenticatedOnly
            fallback={
              <div className="p-6 bg-yellow-500/10 border border-yellow-500/50 rounded-lg">
                <p className="text-sm text-yellow-400">
                  Debes iniciar sesión para solicitar este agente.
                </p>
                <Link
                  href="/auth/login"
                  className="inline-block mt-3 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg text-sm font-medium"
                >
                  Iniciar Sesión
                </Link>
              </div>
            }
          >
            <AgentForm agentId={agent.id} agentName={agent.name} />
          </AuthenticatedOnly>
        </div>

        <AdminOnly>
          <div className="bg-card border border-border rounded-lg p-8">
            <h2 className="text-xl font-semibold mb-4">Panel de Admin</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Como administrador, tendrás acceso a herramientas avanzadas de
              personalización y edición de agentes.
            </p>
            <ReplitStudioPlaceholder />
          </div>
        </AdminOnly>
      </div>
    </div>
  );
}
