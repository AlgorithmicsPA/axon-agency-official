"use client";

import { MessageCircle, Users, TrendingUp } from "lucide-react";

export default function CommentsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-cyan-400">Comentarios</h1>
        <p className="text-muted-foreground">Gestión de comentarios y moderación</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <MessageCircle className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Total Comentarios</p>
          </div>
          <p className="text-3xl font-bold">0</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Users className="text-purple-400" size={20} />
            <p className="text-sm font-medium">Pendientes</p>
          </div>
          <p className="text-3xl font-bold">0</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-green-400" size={20} />
            <p className="text-sm font-medium">Aprobados</p>
          </div>
          <p className="text-3xl font-bold">0</p>
        </div>
      </div>

      <div className="bg-card p-12 rounded-lg border border-border text-center">
        <MessageCircle className="mx-auto mb-4 text-muted-foreground" size={48} />
        <h3 className="text-lg font-bold mb-2">Módulo de Comentarios</h3>
        <p className="text-muted-foreground mb-4">
          Esta funcionalidad estará disponible próximamente.
        </p>
        <p className="text-sm text-muted-foreground">
          Podrás gestionar comentarios de tus posts, moderar contenido y responder a tu audiencia.
        </p>
      </div>
    </div>
  );
}
