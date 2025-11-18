"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

interface AgentFormProps {
  agentId: string;
  agentName: string;
}

export function AgentForm({ agentId, agentName }: AgentFormProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [description, setDescription] = useState("");
  const [contactEmail, setContactEmail] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const response = await fetch("/api/catalog/orders", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          agent_id: agentId,
          website_url: websiteUrl,
          description: description,
          contact_email: contactEmail || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al crear la orden");
      }

      const result = await response.json();
      
      router.push(`/agent/orders`);
    } catch (err: any) {
      setError(err.message || "Error al enviar el formulario");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium mb-2">
          URL de tu Sitio Web *
        </label>
        <input
          type="url"
          required
          value={websiteUrl}
          onChange={(e) => setWebsiteUrl(e.target.value)}
          placeholder="https://ejemplo.com"
          className="w-full px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
        <p className="text-xs text-muted-foreground mt-1">
          Pega la URL del sitio que quieres que analicemos
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">
          Descripción del Proyecto *
        </label>
        <textarea
          required
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          placeholder="Describe qué características necesitas o qué mejoras quieres implementar..."
          className="w-full px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 resize-none"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">
          Email de Contacto (opcional)
        </label>
        <input
          type="email"
          value={contactEmail}
          onChange={(e) => setContactEmail(e.target.value)}
          placeholder="tu@email.com"
          className="w-full px-4 py-2 bg-card border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
        />
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      <Button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-cyan-500 hover:bg-cyan-600 text-white"
      >
        {isSubmitting ? "Enviando..." : `Solicitar ${agentName}`}
      </Button>
    </form>
  );
}
