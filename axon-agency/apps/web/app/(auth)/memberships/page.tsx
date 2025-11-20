"use client";

import { Users, CreditCard, TrendingUp, Star } from "lucide-react";

export default function MembershipsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-cyan-400">Membresías</h1>
        <p className="text-muted-foreground">Sistema de membresías y suscripciones</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Users className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Miembros Activos</p>
          </div>
          <p className="text-3xl font-bold">0</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <CreditCard className="text-green-400" size={20} />
            <p className="text-sm font-medium">Ingresos MRR</p>
          </div>
          <p className="text-3xl font-bold">$0</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-purple-400" size={20} />
            <p className="text-sm font-medium">Crecimiento</p>
          </div>
          <p className="text-3xl font-bold">0%</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Star className="text-yellow-400" size={20} />
            <p className="text-sm font-medium">Planes</p>
          </div>
          <p className="text-3xl font-bold">0</p>
        </div>
      </div>

      <div className="bg-card p-12 rounded-lg border border-border text-center">
        <CreditCard className="mx-auto mb-4 text-muted-foreground" size={48} />
        <h3 className="text-lg font-bold mb-2">Sistema de Membresías</h3>
        <p className="text-muted-foreground mb-4">
          Esta funcionalidad estará disponible próximamente.
        </p>
        <p className="text-sm text-muted-foreground">
          Podrás crear planes de suscripción, gestionar pagos recurrentes y administrar tu comunidad de miembros.
        </p>
      </div>
    </div>
  );
}
