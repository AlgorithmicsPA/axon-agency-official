"use client";

import { useAppStore } from "@/lib/store";
import { Wifi, WifiOff } from "lucide-react";

export function Topbar() {
  const wsStatus = useAppStore((state) => state.wsStatus);

  return (
    <header className="h-16 border-b border-border bg-card px-6 flex items-center justify-between">
      <div className="text-sm text-muted-foreground">
        Sistema de Control de Agencia IA
      </div>
      
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2">
          {wsStatus === "connected" ? (
            <>
              <Wifi size={18} className="text-green-500" />
              <span className="text-sm text-green-500">Conectado</span>
            </>
          ) : (
            <>
              <WifiOff size={18} className="text-red-500" />
              <span className="text-sm text-red-500">Desconectado</span>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
