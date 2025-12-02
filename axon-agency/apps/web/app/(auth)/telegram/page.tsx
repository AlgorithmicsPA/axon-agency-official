"use client";

import { useEffect, useState } from "react";
import { useApiClient } from "@/lib/api";
import { Send, Check, X, Copy, ExternalLink } from "lucide-react";

export default function TelegramPage() {
  const api = useApiClient();
  const [status, setStatus] = useState<any>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await api.get<any>("/api/integrations/telegram/status");
      setStatus(res);
    } catch (error) {
      console.error("Error fetching Telegram status:", error);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-blue-400">Telegram Integration</h1>
          <p className="text-muted-foreground">Conecta tu bot de Telegram</p>
        </div>
      </div>

      {status && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-card p-6 rounded-lg border border-border">
              <div className="flex items-center gap-3 mb-4">
                <Send className="text-blue-400" size={24} />
                <div>
                  <p className="text-sm text-muted-foreground">Estado</p>
                  <p className="text-lg font-bold flex items-center gap-2">
                    {status.enabled ? (
                      <>
                        <Check className="text-green-400" size={20} />
                        Activo
                      </>
                    ) : (
                      <>
                        <X className="text-red-400" size={20} />
                        Inactivo
                      </>
                    )}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-card p-6 rounded-lg border border-border">
              <div className="flex items-center gap-3">
                <ExternalLink className="text-cyan-400" size={24} />
                <div>
                  <p className="text-sm text-muted-foreground">Tipo</p>
                  <p className="text-lg font-bold">Telegram Bot API</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-card p-6 rounded-lg border border-blue-500/20">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
              <Send className="text-blue-400" size={20} />
              Configuración del Webhook
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Webhook URL</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={window.location.origin + status.webhook_url}
                    readOnly
                    className="flex-1 px-4 py-2 bg-accent rounded-lg border border-border"
                  />
                  <button
                    onClick={() => copyToClipboard(window.location.origin + status.webhook_url)}
                    className="px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 rounded-lg transition-colors flex items-center gap-2"
                  >
                    <Copy size={16} />
                    {copied ? 'Copiado!' : 'Copiar'}
                  </button>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Configura esta URL en tu bot de Telegram usando la API de Bot
                </p>
              </div>
            </div>
          </div>

          <div className="bg-card p-6 rounded-lg border border-border">
            <h2 className="text-lg font-bold mb-4">Pasos para Configurar</h2>
            <ol className="space-y-3 list-decimal list-inside text-sm text-muted-foreground">
              <li>Crea un bot con @BotFather en Telegram y obtén el token</li>
              <li>Configura el webhook usando la API de Telegram:
                <code className="block mt-2 p-2 bg-accent rounded text-xs">
                  POST https://api.telegram.org/bot{'<TOKEN>'}/setWebhook
                </code>
              </li>
              <li>En el body, envía: {`{"url": "WEBHOOK_URL_AQUI"}`}</li>
              <li>Verifica que el webhook esté configurado correctamente</li>
              <li>Comienza a interactuar con tu bot</li>
            </ol>
          </div>
        </>
      )}
    </div>
  );
}
