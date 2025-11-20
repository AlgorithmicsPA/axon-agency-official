"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useToast } from "@/components/Toast";

export default function SettingsPage() {
  const { backendUrl, jwtToken, setBackendUrl, setJwtToken } = useAppStore();
  const { showToast } = useToast();
  const [url, setUrl] = useState(backendUrl);
  const [token, setToken] = useState(jwtToken);

  const handleSave = () => {
    setBackendUrl(url);
    setJwtToken(token);
    showToast("Configuración guardada", "success");
  };

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Configuración</h1>
      
      <div className="space-y-4 bg-card p-6 rounded-lg border border-border">
        <div>
          <label className="block text-sm font-medium mb-2">Backend URL</label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full px-4 py-2 bg-accent rounded-lg"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">JWT Token</label>
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full px-4 py-2 bg-accent rounded-lg"
          />
        </div>
        
        <button
          onClick={handleSave}
          className="px-6 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg"
        >
          Guardar
        </button>
      </div>
    </div>
  );
}
