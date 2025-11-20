"use client";

import { useState } from "react";
import { User, Mail, Shield, Key, Save } from "lucide-react";
import { useToast } from "@/components/Toast";

export default function ProfilePage() {
  const { showToast } = useToast();
  const [formData, setFormData] = useState({
    name: "Admin User",
    email: "admin@axon-agency.com",
    role: "admin",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const handleSave = () => {
    if (formData.newPassword && formData.newPassword !== formData.confirmPassword) {
      showToast("Las contraseñas no coinciden", "error");
      return;
    }
    showToast("Perfil actualizado exitosamente", "success");
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-cyan-400">Mi Perfil</h1>
        <p className="text-muted-foreground">Gestiona tu información personal</p>
      </div>

      <div className="bg-card p-8 rounded-lg border border-border">
        <div className="flex items-center gap-4 mb-8">
          <div className="w-24 h-24 rounded-full bg-cyan-500/20 flex items-center justify-center">
            <User size={48} className="text-cyan-400" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">{formData.name}</h2>
            <p className="text-muted-foreground">{formData.email}</p>
            <span className="inline-block mt-2 px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded-full text-sm font-medium">
              {formData.role === 'admin' ? 'Administrador' : 'Usuario'}
            </span>
          </div>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <User size={20} className="text-cyan-400" />
              Información Personal
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nombre Completo</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-cyan-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <div className="flex items-center gap-2">
                  <Mail size={20} className="text-muted-foreground" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="flex-1 px-4 py-2 bg-accent rounded-lg border border-border focus:border-cyan-500 outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Rol</label>
                <div className="flex items-center gap-2">
                  <Shield size={20} className="text-muted-foreground" />
                  <input
                    type="text"
                    value={formData.role === 'admin' ? 'Administrador' : 'Usuario'}
                    readOnly
                    className="flex-1 px-4 py-2 bg-accent rounded-lg border border-border opacity-50 cursor-not-allowed"
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-border pt-6">
            <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Key size={20} className="text-purple-400" />
              Cambiar Contraseña
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Contraseña Actual</label>
                <input
                  type="password"
                  value={formData.currentPassword}
                  onChange={(e) => setFormData({ ...formData, currentPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-cyan-500 outline-none"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Nueva Contraseña</label>
                <input
                  type="password"
                  value={formData.newPassword}
                  onChange={(e) => setFormData({ ...formData, newPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-cyan-500 outline-none"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Confirmar Nueva Contraseña</label>
                <input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-cyan-500 outline-none"
                  placeholder="••••••••"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              onClick={handleSave}
              className="flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-colors"
            >
              <Save size={20} />
              Guardar Cambios
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
