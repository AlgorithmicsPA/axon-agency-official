"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useApiClient } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useToast } from "@/hooks/use-toast";
import { QAStatusBadge } from "@/components/orders/QAStatusBadge";
import { DeliverableCard } from "@/components/orders/DeliverableCard";
import { AgentBlueprintCard } from "@/components/orders/AgentBlueprintCard";
import { AgentArtifactsCard } from "@/components/orders/AgentArtifactsCard";
import { AdminOnly } from "@/components/auth/RoleGuard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  ArrowLeft, 
  Package, 
  User, 
  Calendar,
  Activity,
  AlertCircle,
  Loader2,
  CheckCircle2,
  Clock,
  TrendingUp,
  MessageCircle,
  Share2
} from "lucide-react";

interface OrderDetailResponse {
  id: string;
  order_number: string;
  tipo_producto: string;
  nombre_producto: string;
  estado: string;
  progreso: number;
  prioridad: string;
  tags: string[];
  asignado_a: string | null;
  session_id: string | null;
  cliente_id: string | null;
  datos_cliente: Record<string, any>;
  plan: Record<string, any> | null;
  logs: Array<Record<string, any>>;
  repo_url: string | null;
  deploy_url: string | null;
  construido_en: string | null;
  qa_status: "ok" | "warn" | "fail" | null;
  qa_messages: string[] | null;
  qa_checked_files: string[] | null;
  qa_ejecutado_en: string | null;
  deliverable_generado: boolean;
  deliverable_metadata: {
    order_number: string;
    tipo_producto: string;
    qa_status: string | null;
    construido_en: string;
    archivos: string[];
  } | null;
  deliverable_generado_en: string | null;
  agent_blueprint: Record<string, any> | null;
  resultado: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  planificado_at: string | null;
  construccion_iniciada_at: string | null;
  qa_iniciada_at: string | null;
  entregado_at: string | null;
  notas_internas: string;
  deploy_history: Array<any> | null;
  ayrshare_enabled?: boolean;
}

interface QAStatusResponse {
  order_id: string;
  order_number: string;
  qa_executed: boolean;
  qa_status: "ok" | "warn" | "fail" | null;
  qa_messages: string[] | null;
  qa_checked_files: string[] | null;
  qa_ejecutado_en: string | null;
}

interface DeliverableResponse {
  order_id: string;
  order_number: string;
  deliverable_generado: boolean;
  deliverable_metadata: {
    order_number: string;
    tipo_producto: string;
    qa_status: string | null;
    construido_en: string;
    archivos: string[];
  } | null;
  deliverable_generado_en: string | null;
}

export default function OrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApiClient();
  const { isAdmin } = useAuth();
  const { showToast } = useToast();
  const orderId = params.id as string;

  const [order, setOrder] = useState<OrderDetailResponse | null>(null);
  const [qaData, setQaData] = useState<QAStatusResponse | null>(null);
  const [deliverableData, setDeliverableData] = useState<DeliverableResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deployWhatsAppLoading, setDeployWhatsAppLoading] = useState(false);
  const [deploySocialLoading, setDeploySocialLoading] = useState(false);

  const fetchOrderData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [orderRes, qaRes, deliverableRes] = await Promise.all([
        api.get(`/api/orders/${orderId}`),
        api.get(`/api/factory/orders/${orderId}/qa`),
        api.get(`/api/factory/orders/${orderId}/deliverable`)
      ]);

      setOrder(orderRes.data);
      setQaData(qaRes.data);
      setDeliverableData(deliverableRes.data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError("Order not found");
      } else {
        setError(err.response?.data?.detail || "Failed to load order data");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderData();
  }, [orderId]);

  const handleDeployToWhatsApp = async () => {
    setDeployWhatsAppLoading(true);
    try {
      await api.post(`/api/orders/${orderId}/deploy/whatsapp`);
      showToast("📲 Deploy enviado a n8n correctamente", "success");
      await fetchOrderData();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Error al enviar deploy";
      showToast(errorMessage, "error");
    } finally {
      setDeployWhatsAppLoading(false);
    }
  };

  const handleDeployToSocial = async () => {
    setDeploySocialLoading(true);
    try {
      await api.post(`/api/orders/${orderId}/deploy/social`);
      showToast("🚀 Social deploy enviado a Ayrshare correctamente", "success");
      await fetchOrderData();
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || "Error al enviar deploy";
      showToast(errorMessage, "error");
    } finally {
      setDeploySocialLoading(false);
    }
  };

  const shouldShowWhatsAppDeployButton = 
    isAdmin &&
    order?.tipo_producto.toLowerCase().includes("whatsapp") &&
    order?.estado === "listo" &&
    order?.qa_status === "ok";

  const shouldShowSocialDeployButton = 
    isAdmin &&
    order?.ayrshare_enabled &&
    order?.tipo_producto.toLowerCase().includes("social") &&
    order?.estado === "listo" &&
    order?.qa_status === "ok";

  const formatDeployDate = (dateString: string): string => {
    const date = new Date(dateString);
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const day = date.getDate().toString().padStart(2, '0');
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${day} ${month} ${year}, ${hours}:${minutes}`;
  };

  const getEstadoBadgeVariant = (estado: string): "default" | "secondary" | "outline" | "destructive" => {
    const variants: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
      nuevo: "secondary",
      planificacion: "outline",
      construccion: "default",
      qa: "outline",
      listo: "default",
      entregado: "default",
      fallido: "destructive",
      cancelado: "destructive"
    };
    return variants[estado] || "outline";
  };

  const getPrioridadColor = (prioridad: string) => {
    const colors: Record<string, string> = {
      baja: "text-gray-400",
      normal: "text-blue-400",
      alta: "text-orange-400",
      urgente: "text-red-400"
    };
    return colors[prioridad] || "text-gray-400";
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <Loader2 className="animate-spin text-cyan-400" size={48} />
        <p className="text-muted-foreground">Loading order details...</p>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertCircle className="text-red-400" size={48} />
        <h2 className="text-xl font-semibold text-red-400">{error || "Order not found"}</h2>
        <Button onClick={() => router.back()} variant="outline">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-6 overflow-auto p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button onClick={() => router.back()} variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-cyan-400">{order.order_number}</h1>
            <p className="text-muted-foreground mt-1">{order.nombre_producto}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={getEstadoBadgeVariant(order.estado)} className="text-sm">
            {order.estado.toUpperCase()}
          </Badge>
          <Badge variant="outline" className={`text-sm ${getPrioridadColor(order.prioridad)}`}>
            {order.prioridad.toUpperCase()}
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5 text-cyan-400" />
                Order Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Product Type</p>
                  <p className="font-semibold">{order.tipo_producto}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Product Name</p>
                  <p className="font-semibold">{order.nombre_producto}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Status</p>
                  <p className="font-semibold">{order.estado}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Priority</p>
                  <p className={`font-semibold ${getPrioridadColor(order.prioridad)}`}>
                    {order.prioridad}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm text-muted-foreground mb-2">Progress</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-accent rounded-full h-2 overflow-hidden">
                    <div 
                      className="bg-cyan-500 h-full transition-all duration-300"
                      style={{ width: `${order.progreso}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-cyan-400">{order.progreso}%</span>
                </div>
              </div>

              {order.tags.length > 0 && (
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Tags</p>
                  <div className="flex flex-wrap gap-2">
                    {order.tags.map((tag, idx) => (
                      <Badge key={idx} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5 text-cyan-400" />
                Client Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {order.cliente_id && (
                  <div>
                    <p className="text-sm text-muted-foreground">Client ID</p>
                    <p className="font-mono text-sm">{order.cliente_id}</p>
                  </div>
                )}
                {Object.keys(order.datos_cliente).length > 0 && (
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">Client Data</p>
                    <div className="bg-accent rounded-lg p-3 space-y-2">
                      {Object.entries(order.datos_cliente).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-muted-foreground">{key}:</span>
                          <span className="font-mono">
                            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-cyan-400" />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">Created:</span>
                  <span className="font-semibold">
                    {new Date(order.created_at).toLocaleString()}
                  </span>
                </div>
                
                {order.planificado_at && (
                  <div className="flex items-center gap-3 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-green-400" />
                    <span className="text-muted-foreground">Planned:</span>
                    <span className="font-semibold">
                      {new Date(order.planificado_at).toLocaleString()}
                    </span>
                  </div>
                )}
                
                {order.construccion_iniciada_at && (
                  <div className="flex items-center gap-3 text-sm">
                    <Activity className="h-4 w-4 text-blue-400" />
                    <span className="text-muted-foreground">Construction Started:</span>
                    <span className="font-semibold">
                      {new Date(order.construccion_iniciada_at).toLocaleString()}
                    </span>
                  </div>
                )}
                
                {order.construido_en && (
                  <div className="flex items-center gap-3 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-cyan-400" />
                    <span className="text-muted-foreground">Built:</span>
                    <span className="font-semibold">
                      {new Date(order.construido_en).toLocaleString()}
                    </span>
                  </div>
                )}
                
                {order.qa_ejecutado_en && (
                  <div className="flex items-center gap-3 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-purple-400" />
                    <span className="text-muted-foreground">QA Executed:</span>
                    <span className="font-semibold">
                      {new Date(order.qa_ejecutado_en).toLocaleString()}
                    </span>
                  </div>
                )}
                
                {order.entregado_at && (
                  <div className="flex items-center gap-3 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-green-400" />
                    <span className="text-muted-foreground">Delivered:</span>
                    <span className="font-semibold">
                      {new Date(order.entregado_at).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {order.asignado_a && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-cyan-400" />
                  Assignment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div>
                  <p className="text-sm text-muted-foreground">Assigned To</p>
                  <p className="font-semibold">{order.asignado_a}</p>
                </div>
                {order.session_id && (
                  <div>
                    <p className="text-sm text-muted-foreground">Session ID</p>
                    <p className="font-mono text-sm">{order.session_id}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quality Assurance</CardTitle>
              <CardDescription>
                Automated validation results from Axon 88 Builder v2
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground mb-2">Status</p>
                <QAStatusBadge 
                  status={qaData?.qa_status || null}
                  messages={qaData?.qa_messages || []}
                />
              </div>

              {qaData?.qa_executed && qaData.qa_messages && qaData.qa_messages.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">Validation Messages</p>
                  <div className="space-y-2">
                    {qaData.qa_messages.map((msg, idx) => (
                      <div 
                        key={idx}
                        className="flex items-start gap-2 text-sm p-2 rounded-md bg-muted/50"
                      >
                        <CheckCircle2 className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                        <span className="text-xs">{msg}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {qaData?.qa_checked_files && qaData.qa_checked_files.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-muted-foreground mb-2">
                    Checked Files ({qaData.qa_checked_files.length})
                  </p>
                  <div className="space-y-1.5">
                    {qaData.qa_checked_files.map((file, idx) => (
                      <div 
                        key={idx}
                        className="flex items-center gap-2 text-sm p-2 rounded-md bg-muted/50"
                      >
                        <CheckCircle2 className="h-3.5 w-3.5 text-cyan-400 flex-shrink-0" />
                        <span className="font-mono text-xs">{file}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {qaData?.qa_ejecutado_en && (
                <div className="pt-2 border-t">
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    <span>Executed: {new Date(qaData.qa_ejecutado_en).toLocaleString()}</span>
                  </div>
                </div>
              )}

              {!qaData?.qa_executed && (
                <div className="text-center py-4">
                  <p className="text-sm text-muted-foreground">
                    QA validation pending. Will run automatically when build completes.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <DeliverableCard
            orderNumber={order.order_number}
            tipoProducto={order.tipo_producto}
            deliverableGenerado={deliverableData?.deliverable_generado || false}
            deliverableMetadata={deliverableData?.deliverable_metadata}
            deliverableGeneradoEn={deliverableData?.deliverable_generado_en}
          />

          <AdminOnly>
            <AgentArtifactsCard 
              deliverableMetadata={deliverableData?.deliverable_metadata}
            />
          </AdminOnly>

          <AdminOnly>
            {(shouldShowWhatsAppDeployButton || shouldShowSocialDeployButton) && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium">Deploy Actions</CardTitle>
                  <CardDescription>
                    Deploy this order to external channels
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {shouldShowWhatsAppDeployButton && (
                    <Button
                      onClick={handleDeployToWhatsApp}
                      disabled={deployWhatsAppLoading}
                      className="w-full"
                      variant="default"
                    >
                      {deployWhatsAppLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Deploying to WhatsApp...
                        </>
                      ) : (
                        <>
                          <MessageCircle className="mr-2 h-4 w-4" />
                          Deploy to WhatsApp
                        </>
                      )}
                    </Button>
                  )}

                  {shouldShowSocialDeployButton && (
                    <Button
                      onClick={handleDeployToSocial}
                      disabled={deploySocialLoading}
                      className="w-full"
                      variant="default"
                    >
                      {deploySocialLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Deploying to Social...
                        </>
                      ) : (
                        <>
                          <Share2 className="mr-2 h-4 w-4" />
                          Deploy to Social (Ayrshare)
                        </>
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}
          </AdminOnly>

          <AdminOnly>
            <AgentBlueprintCard agentBlueprint={order.agent_blueprint} />
          </AdminOnly>

          <AdminOnly>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Deploy History</CardTitle>
                <CardDescription>
                  History of deployment events to external channels
                </CardDescription>
              </CardHeader>
              <CardContent>
                {!order.deploy_history || order.deploy_history.length === 0 ? (
                  <div className="text-center py-6">
                    <p className="text-sm text-muted-foreground">
                      No se han realizado deploys aún
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {[...order.deploy_history].reverse().map((event, idx) => {
                      const getStatusBadge = (status: string) => {
                        if (status === "success") {
                          return (
                            <Badge className="gap-1.5 bg-green-500/10 text-green-500 border-green-500/20">
                              <CheckCircle2 className="h-3 w-3" />
                              Success
                            </Badge>
                          );
                        } else if (status === "failed") {
                          return (
                            <Badge className="gap-1.5 bg-red-500/10 text-red-500 border-red-500/20">
                              <AlertCircle className="h-3 w-3" />
                              Failed
                            </Badge>
                          );
                        } else {
                          return (
                            <Badge className="gap-1.5 bg-yellow-500/10 text-yellow-500 border-yellow-500/20">
                              <Clock className="h-3 w-3" />
                              Pending
                            </Badge>
                          );
                        }
                      };

                      const getChannelIcon = (channel: string) => {
                        if (channel === "whatsapp") {
                          return <MessageCircle className="h-4 w-4 text-cyan-400" />;
                        } else if (channel === "social") {
                          return <Share2 className="h-4 w-4 text-purple-400" />;
                        }
                        return <Activity className="h-4 w-4 text-gray-400" />;
                      };

                      return (
                        <div
                          key={idx}
                          className="p-3 rounded-lg border bg-muted/30 space-y-2"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              {getChannelIcon(event.channel)}
                              <span className="text-sm font-medium">{event.channel}</span>
                              {event.target_system && (
                                <span className="text-xs text-muted-foreground">
                                  → {event.target_system}
                                </span>
                              )}
                            </div>
                            {getStatusBadge(event.status)}
                          </div>
                          
                          <div className="space-y-1 text-xs text-muted-foreground">
                            <div className="flex items-center gap-2">
                              <Clock className="h-3 w-3" />
                              <span>Requested: {formatDeployDate(event.requested_at)}</span>
                            </div>
                            
                            {event.completed_at && (
                              <div className="flex items-center gap-2">
                                <CheckCircle2 className="h-3 w-3 text-green-400" />
                                <span>Completed: {formatDeployDate(event.completed_at)}</span>
                              </div>
                            )}

                            {event.platforms && event.platforms.length > 0 && (
                              <div className="flex items-center gap-2">
                                <Share2 className="h-3 w-3" />
                                <span>Platforms: {event.platforms.join(", ")}</span>
                              </div>
                            )}
                          </div>

                          {event.status === "failed" && event.error_message && (
                            <div className="mt-2 p-2 rounded bg-red-500/10 border border-red-500/20">
                              <p className="text-xs text-red-400">{event.error_message}</p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </AdminOnly>

          {order.repo_url && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Repository</CardTitle>
              </CardHeader>
              <CardContent>
                <a 
                  href={order.repo_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:text-cyan-300 text-sm break-all underline"
                >
                  {order.repo_url}
                </a>
              </CardContent>
            </Card>
          )}

          {order.deploy_url && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Deployment</CardTitle>
              </CardHeader>
              <CardContent>
                <a 
                  href={order.deploy_url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:text-cyan-300 text-sm break-all underline"
                >
                  {order.deploy_url}
                </a>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
