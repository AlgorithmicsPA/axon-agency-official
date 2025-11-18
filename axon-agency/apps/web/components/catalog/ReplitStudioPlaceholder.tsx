"use client";

import { Code2, AlertCircle } from "lucide-react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { REPLIT_STUDIO_URL } from "@/config/replit";

export function ReplitStudioPlaceholder() {
  if (!REPLIT_STUDIO_URL) {
    return (
      <Card className="mt-4 border-yellow-500/30 bg-yellow-500/5">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/10 rounded-lg">
              <AlertCircle className="h-5 w-5 text-yellow-400" />
            </div>
            <h3 className="text-lg font-semibold text-yellow-400">
              Replit Studio no configurado
            </h3>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Para habilitar el estudio embebido, configura la variable de entorno{" "}
            <code className="px-2 py-1 bg-muted rounded text-cyan-400">
              NEXT_PUBLIC_REPLIT_STUDIO_URL
            </code>{" "}
            con la URL de tu Repl.
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            Ejemplo: <code className="text-cyan-400">https://replit.com/@USUARIO/NOMBRE-DEL-REPL?embed=true</code>
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mt-4 border-cyan-500/30 bg-cyan-500/5">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-cyan-500/10 rounded-lg">
            <Code2 className="h-5 w-5 text-cyan-400" />
          </div>
          <h3 className="text-lg font-semibold text-cyan-400">
            Replit Studio (Admin)
          </h3>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <iframe
          src={REPLIT_STUDIO_URL}
          className="w-full h-[600px] rounded-xl border border-cyan-500/20"
          loading="lazy"
          allow="clipboard-read; clipboard-write; microphone; camera"
          title="Replit Studio"
        />
        <p className="text-xs text-muted-foreground italic">
          ⚠️ Este estudio es solo para uso interno del equipo. No compartas esta vista con clientes finales.
        </p>
      </CardContent>
    </Card>
  );
}
