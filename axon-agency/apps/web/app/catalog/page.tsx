"use client";

import { useState, useEffect } from "react";
import { AgentCard } from "@/components/catalog/AgentCard";
import { Store, Filter } from "lucide-react";

interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  pricing: string;
}

export default function CatalogPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch("/api/catalog/agents");
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (error) {
      console.error("Error fetching agents:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const categories = ["all", ...Array.from(new Set(agents.map((a) => a.category)))];

  const filteredAgents =
    selectedCategory === "all"
      ? agents
      : agents.filter((a) => a.category === selectedCategory);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-cyan-500/10 rounded-lg">
            <Store className="h-6 w-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Catálogo de Agentes</h1>
            <p className="text-muted-foreground">
              Selecciona un agente para automatizar tu negocio
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Filter className="h-4 w-4 text-muted-foreground" />
        <div className="flex gap-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? "bg-cyan-500 text-white"
                  : "bg-card border border-border hover:border-cyan-500/50"
              }`}
            >
              {category === "all" ? "Todos" : category}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="h-48 bg-card border border-border rounded-lg animate-pulse" />
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents.map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>

          {filteredAgents.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">
                No se encontraron agentes en esta categoría
              </p>
            </div>
          )}
        </>
      )}

      <div className="mt-8 p-6 bg-card border border-border rounded-lg">
        <h3 className="font-semibold mb-2">¿Cómo funciona?</h3>
        <ol className="space-y-2 text-sm text-muted-foreground">
          <li>1. Selecciona el agente que mejor se adapte a tus necesidades</li>
          <li>2. Completa el formulario con los detalles de tu proyecto</li>
          <li>3. Nuestro sistema procesará tu solicitud automáticamente</li>
          <li>4. Recibe tu producto listo con QA incluido</li>
        </ol>
      </div>
    </div>
  );
}
