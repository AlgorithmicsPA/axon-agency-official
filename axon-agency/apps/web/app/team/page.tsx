"use client";

import { Users, UserPlus, Shield, Award } from "lucide-react";

export default function TeamPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-cyan-400">Mi Equipo</h1>
        <p className="text-muted-foreground">Gestión de usuarios y permisos</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Users className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Total Miembros</p>
          </div>
          <p className="text-3xl font-bold">1</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="text-purple-400" size={20} />
            <p className="text-sm font-medium">Administradores</p>
          </div>
          <p className="text-3xl font-bold">1</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <UserPlus className="text-green-400" size={20} />
            <p className="text-sm font-medium">Editores</p>
          </div>
          <p className="text-3xl font-bold">0</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Award className="text-yellow-400" size={20} />
            <p className="text-sm font-medium">Invitaciones</p>
          </div>
          <p className="text-3xl font-bold">0</p>
        </div>
      </div>

      <div className="bg-card p-12 rounded-lg border border-border text-center">
        <Users className="mx-auto mb-4 text-muted-foreground" size={48} />
        <h3 className="text-lg font-bold mb-2">Gestión de Equipo</h3>
        <p className="text-muted-foreground mb-4">
          Esta funcionalidad estará disponible próximamente.
        </p>
        <p className="text-sm text-muted-foreground">
          Podrás invitar colaboradores, asignar roles y permisos, y gestionar el acceso a tu agencia.
        </p>
      </div>
    </div>
  );
}
