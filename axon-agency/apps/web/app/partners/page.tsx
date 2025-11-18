"use client";

import { Handshake, Users, DollarSign, TrendingUp } from "lucide-react";

export default function PartnersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-cyan-400">Asociados</h1>
        <p className="text-muted-foreground">Red de socios y colaboradores</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Handshake className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Socios Activos</p>
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
            <DollarSign className="text-green-400" size={20} />
            <p className="text-sm font-medium">Comisiones</p>
          </div>
          <p className="text-3xl font-bold">$0</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-yellow-400" size={20} />
            <p className="text-sm font-medium">Conversiones</p>
          </div>
          <p className="text-3xl font-bold">0</p>
        </div>
      </div>

      <div className="bg-card p-12 rounded-lg border border-border text-center">
        <Handshake className="mx-auto mb-4 text-muted-foreground" size={48} />
        <h3 className="text-lg font-bold mb-2">Programa de Asociados</h3>
        <p className="text-muted-foreground mb-4">
          Esta funcionalidad estará disponible próximamente.
        </p>
        <p className="text-sm text-muted-foreground">
          Podrás gestionar tu red de socios, rastrear comisiones y expandir tu alcance a través de colaboraciones estratégicas.
        </p>
      </div>
    </div>
  );
}
