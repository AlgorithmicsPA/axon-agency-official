"use client";

import { useState, useEffect } from "react";
import { useApiClient } from "@/lib/api";
import { AdminOnly } from "@/components/auth/RoleGuard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Circle,
  RefreshCw,
  Database,
  MessageCircle,
  Share2,
  Send,
  Loader2,
  Activity,
  ShieldX
} from "lucide-react";

interface IntegrationHealth {
  name: string;
  status: "healthy" | "degraded" | "disabled";
  message: string | null;
  last_activity: string | null;
  details?: any;
}

interface HealthResponse {
  overall_status: "healthy" | "degraded" | "disabled";
  timestamp: string;
  integrations: IntegrationHealth[];
}

const integrationIcons: Record<string, any> = {
  mongodb: Database,
  whatsapp_core: MessageCircle,
  whatsapp_sales_agent: MessageCircle,
  social: Share2,
  telegram: Send,
};

const integrationNames: Record<string, string> = {
  mongodb: "MongoDB",
  whatsapp_core: "WhatsApp Core",
  whatsapp_sales_agent: "WhatsApp Sales Agent",
  social: "Social Media",
  telegram: "Telegram",
};

const optionalIntegrationNames: Record<string, string> = {
  melvis: "Melvis",
  tavily: "Tavily",
  linkedin: "LinkedIn",
  stripe: "Stripe",
  calcom: "Cal.com",
};

function getStatusIcon(status: "healthy" | "degraded" | "disabled") {
  switch (status) {
    case "healthy":
      return CheckCircle2;
    case "degraded":
      return AlertTriangle;
    case "disabled":
      return Circle;
  }
}

function getStatusColor(status: "healthy" | "degraded" | "disabled") {
  switch (status) {
    case "healthy":
      return "text-green-500";
    case "degraded":
      return "text-yellow-500";
    case "disabled":
      return "text-gray-500";
  }
}

function getStatusBgColor(status: "healthy" | "degraded" | "disabled") {
  switch (status) {
    case "healthy":
      return "bg-green-500/10 text-green-500 border-green-500/50";
    case "degraded":
      return "bg-yellow-500/10 text-yellow-500 border-yellow-500/50";
    case "disabled":
      return "bg-gray-500/10 text-gray-500 border-gray-500/50";
  }
}

function formatTimestamp(timestamp: string | null): string {
  if (!timestamp) return "N/A";
  try {
    const date = new Date(timestamp);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return timestamp;
  }
}

export default function IntegrationsHealthPage() {
  const api = useApiClient();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchHealth = async () => {
    setRefreshing(true);
    setError(null);
    try {
      const res = await api.get<any>("/api/integrations/health");
      setHealth(res);
    } catch (err: any) {
      console.error("Error fetching health:", err);
      setError(err.response?.data?.detail || "Failed to fetch integration health");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const OverallStatusIcon = health ? getStatusIcon(health.overall_status) : Circle;
  const overallStatusColor = health ? getStatusColor(health.overall_status) : "text-gray-500";

  const unauthorizedFallback = (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <ShieldX className="h-16 w-16 text-red-400" />
      <h2 className="text-2xl font-semibold text-red-400">Access Denied</h2>
      <p className="text-muted-foreground">
        This dashboard is only accessible to administrators.
      </p>
    </div>
  );

  return (
    <AdminOnly fallback={unauthorizedFallback}>
      <div className="h-full flex flex-col space-y-6 overflow-auto p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3">
              <Activity className="h-8 w-8 text-cyan-400" />
              <h1 className="text-3xl font-bold">Estado de Integraciones</h1>
            </div>
            <p className="text-muted-foreground mt-2">
              Monitoreo en tiempo real de todos los canales y servicios
            </p>
          </div>
          <Button
            onClick={fetchHealth}
            variant="outline"
            size="sm"
            disabled={refreshing}
          >
            <RefreshCw
              className={`mr-2 h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
            />
            Refresh
          </Button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="animate-spin text-cyan-400" size={48} />
            <p className="text-muted-foreground">Loading integration status...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <XCircle className="text-red-400" size={48} />
            <h2 className="text-xl font-semibold text-red-400">{error}</h2>
            <Button onClick={fetchHealth} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </div>
        ) : health ? (
          <>
            <Card className={`border-2 ${overallStatusColor.replace('text-', 'border-')}/50`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <OverallStatusIcon className={`h-8 w-8 ${overallStatusColor}`} />
                  <span>Overall Status: {health.overall_status.toUpperCase()}</span>
                </CardTitle>
                <CardDescription>
                  Last updated: {formatTimestamp(health.timestamp)}
                </CardDescription>
              </CardHeader>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {health.integrations.map((integration) => {
                const Icon = integrationIcons[integration.name] || Circle;
                const StatusIcon = getStatusIcon(integration.status);
                const statusColor = getStatusColor(integration.status);
                const statusBgColor = getStatusBgColor(integration.status);
                const friendlyName = integrationNames[integration.name] || integration.name;

                return (
                  <Card key={integration.name} className="border-border">
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Icon className="h-5 w-5 text-cyan-400" />
                          <span className="text-lg">{friendlyName}</span>
                        </div>
                        <Badge
                          variant="outline"
                          className={statusBgColor}
                        >
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {integration.status}
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      {integration.message && (
                        <p className="text-sm text-muted-foreground">
                          {integration.message}
                        </p>
                      )}

                      {integration.last_activity && (
                        <div className="text-xs text-muted-foreground">
                          <span className="font-medium">Last activity:</span>{" "}
                          {formatTimestamp(integration.last_activity)}
                        </div>
                      )}

                      {integration.details && integration.name === "whatsapp_sales_agent" && integration.details.optional_integrations && (
                        <Accordion type="single" collapsible className="w-full">
                          <AccordionItem value="details" className="border-border">
                            <AccordionTrigger className="text-sm hover:no-underline">
                              Optional Integrations
                            </AccordionTrigger>
                            <AccordionContent>
                              <div className="space-y-2 pt-2">
                                {Object.entries(integration.details.optional_integrations).map(
                                  ([key, enabled]) => (
                                    <div
                                      key={key}
                                      className="flex items-center justify-between text-sm"
                                    >
                                      <span className="text-muted-foreground">
                                        {optionalIntegrationNames[key] || key}
                                      </span>
                                      <span>
                                        {enabled ? (
                                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                                        ) : (
                                          <XCircle className="h-4 w-4 text-gray-500" />
                                        )}
                                      </span>
                                    </div>
                                  )
                                )}
                              </div>
                            </AccordionContent>
                          </AccordionItem>
                        </Accordion>
                      )}

                      {integration.details && integration.name === "social" && (
                        <Accordion type="single" collapsible className="w-full">
                          <AccordionItem value="details" className="border-border">
                            <AccordionTrigger className="text-sm hover:no-underline">
                              Details
                            </AccordionTrigger>
                            <AccordionContent>
                              <div className="space-y-2 pt-2 text-sm">
                                {integration.details.provider && (
                                  <div>
                                    <span className="font-medium">Provider:</span>{" "}
                                    {integration.details.provider}
                                  </div>
                                )}
                                {integration.details.platforms && (
                                  <div>
                                    <span className="font-medium">Platforms:</span>{" "}
                                    {integration.details.platforms.join(", ")}
                                  </div>
                                )}
                                {integration.details.rate_limit && (
                                  <div>
                                    <span className="font-medium">Rate Limit:</span>{" "}
                                    {integration.details.rate_limit.remaining || "N/A"} /{" "}
                                    {integration.details.rate_limit.limit || "N/A"}
                                  </div>
                                )}
                              </div>
                            </AccordionContent>
                          </AccordionItem>
                        </Accordion>
                      )}

                      {integration.details && integration.name === "mongodb" && integration.details.database && (
                        <div className="text-xs text-muted-foreground">
                          <span className="font-medium">Database:</span>{" "}
                          {integration.details.database}
                        </div>
                      )}

                      {integration.details && integration.name === "telegram" && (
                        <Accordion type="single" collapsible className="w-full">
                          <AccordionItem value="details" className="border-border">
                            <AccordionTrigger className="text-sm hover:no-underline">
                              Details
                            </AccordionTrigger>
                            <AccordionContent>
                              <div className="space-y-2 pt-2 text-sm">
                                <div className="flex items-center justify-between">
                                  <span className="text-muted-foreground">Bot Token</span>
                                  <span>
                                    {integration.details.bot_token_configured ? (
                                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                                    ) : (
                                      <XCircle className="h-4 w-4 text-gray-500" />
                                    )}
                                  </span>
                                </div>
                                <div className="flex items-center justify-between">
                                  <span className="text-muted-foreground">Default Chat ID</span>
                                  <span>
                                    {integration.details.default_chat_id_configured ? (
                                      <CheckCircle2 className="h-4 w-4 text-green-500" />
                                    ) : (
                                      <XCircle className="h-4 w-4 text-gray-500" />
                                    )}
                                  </span>
                                </div>
                              </div>
                            </AccordionContent>
                          </AccordionItem>
                        </Accordion>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </>
        ) : null}
      </div>
    </AdminOnly>
  );
}
