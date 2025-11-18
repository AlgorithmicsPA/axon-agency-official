"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useApiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  ArrowLeft, 
  Package, 
  Calendar,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Clock,
  FileText,
  Construction
} from "lucide-react";

interface OrderDetailResponse {
  id: string;
  order_number: string;
  tipo_producto: string;
  nombre_producto: string;
  estado: string;
  progreso: number;
  datos_cliente: Record<string, any>;
  deliverable_generado: boolean;
  deliverable_metadata: {
    order_number: string;
    tipo_producto: string;
    construido_en: string;
    archivos: string[];
  } | null;
  deliverable_generado_en: string | null;
  created_at: string;
  updated_at: string;
}

export default function TenantOrderDetailPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApiClient();
  const tenantSlug = params.tenantSlug as string;
  const orderId = params.id as string;

  const [order, setOrder] = useState<OrderDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrderData = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await api.get(`/api/orders/${orderId}`);
        setOrder(response.data);
      } catch (err: any) {
        if (err.response?.status === 404) {
          setError("Order not found");
        } else if (err.response?.status === 403) {
          setError("Access denied");
        } else {
          setError(err.response?.data?.detail || "Failed to load order");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchOrderData();
  }, [orderId]);

  const getEstadoBadgeColor = (estado: string): string => {
    const colors: Record<string, string> = {
      nuevo: "bg-blue-500/10 text-blue-500 border-blue-500/20",
      planificacion: "bg-purple-500/10 text-purple-500 border-purple-500/20",
      construccion: "bg-cyan-500/10 text-cyan-500 border-cyan-500/20",
      qa: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
      listo: "bg-green-500/10 text-green-500 border-green-500/20",
      entregado: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
      fallido: "bg-red-500/10 text-red-500 border-red-500/20",
      cancelado: "bg-gray-500/10 text-gray-500 border-gray-500/20"
    };
    return colors[estado] || "";
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getSafeClientData = (datos: Record<string, any>) => {
    const safeKeys = ['sitio_web', 'contacto', 'nombre', 'empresa', 'industria', 'descripcion'];
    const safeData: Record<string, any> = {};
    
    for (const key of safeKeys) {
      if (datos[key]) {
        safeData[key] = datos[key];
      }
    }
    
    return safeData;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <Loader2 className="h-12 w-12 animate-spin text-cyan-400" />
        <p className="text-slate-400">Loading order details...</p>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <AlertCircle className="h-12 w-12 text-red-400" />
        <h2 className="text-xl font-semibold text-red-400">{error || "Order not found"}</h2>
        <Button
          onClick={() => router.push(`/portal/${tenantSlug}/orders`)}
          variant="outline"
          className="bg-slate-900 border-slate-700 text-slate-200 hover:bg-slate-800"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Orders
        </Button>
      </div>
    );
  }

  const safeClientData = getSafeClientData(order.datos_cliente);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            onClick={() => router.push(`/portal/${tenantSlug}/orders`)}
            variant="ghost"
            size="icon"
            className="text-slate-400 hover:text-slate-200"
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-slate-50">{order.order_number}</h1>
            <p className="text-slate-400 mt-1">{order.nombre_producto}</p>
          </div>
        </div>
        <Badge variant="outline" className={getEstadoBadgeColor(order.estado)}>
          {order.estado}
        </Badge>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-50">
                <Package className="h-5 w-5 text-cyan-400" />
                Product Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-slate-400">Product Type</p>
                  <p className="font-semibold text-slate-200">{order.tipo_producto}</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Product Name</p>
                  <p className="font-semibold text-slate-200">{order.nombre_producto}</p>
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-400 mb-2">Progress</p>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div 
                      className="bg-cyan-500 h-full transition-all duration-300"
                      style={{ width: `${order.progreso}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-cyan-400">{order.progreso}%</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {Object.keys(safeClientData).length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-slate-50">
                  <FileText className="h-5 w-5 text-cyan-400" />
                  Order Details
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(safeClientData).map(([key, value]) => (
                    <div key={key}>
                      <p className="text-sm text-slate-400 capitalize">
                        {key.replace(/_/g, ' ')}
                      </p>
                      <p className="font-medium text-slate-200">
                        {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-50">
                <Calendar className="h-5 w-5 text-cyan-400" />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-sm">
                  <Clock className="h-4 w-4 text-slate-400" />
                  <span className="text-slate-400">Created:</span>
                  <span className="font-semibold text-slate-200">
                    {formatDate(order.created_at)}
                  </span>
                </div>
                
                <div className="flex items-center gap-3 text-sm">
                  <Clock className="h-4 w-4 text-slate-400" />
                  <span className="text-slate-400">Last Updated:</span>
                  <span className="font-semibold text-slate-200">
                    {formatDate(order.updated_at)}
                  </span>
                </div>

                {order.deliverable_generado_en && (
                  <div className="flex items-center gap-3 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-green-400" />
                    <span className="text-slate-400">Completed:</span>
                    <span className="font-semibold text-slate-200">
                      {formatDate(order.deliverable_generado_en)}
                    </span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-slate-50">
                <Package className="h-5 w-5 text-cyan-400" />
                Deliverable Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              {order.deliverable_generado ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5 text-green-400" />
                    <span className="font-semibold text-green-400">Ready for Delivery</span>
                  </div>

                  {order.deliverable_metadata && (
                    <>
                      <div>
                        <p className="text-sm text-slate-400 mb-2">Product Type</p>
                        <p className="font-medium text-slate-200">
                          {order.deliverable_metadata.tipo_producto}
                        </p>
                      </div>

                      {order.deliverable_metadata.archivos && order.deliverable_metadata.archivos.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-sm text-slate-400">Archivos disponibles:</p>
                          <ul className="space-y-1">
                            {order.deliverable_metadata.archivos.map((path: string, idx: number) => {
                              // Extract only the filename from the full path
                              const filename = path.split('/').pop() || path;
                              return (
                                <li key={idx} className="text-sm flex items-center gap-2">
                                  <Package className="h-4 w-4 text-green-500" />
                                  <span className="text-slate-300">{filename}</span>
                                </li>
                              );
                            })}
                          </ul>
                        </div>
                      )}

                      {order.deliverable_metadata.construido_en && (
                        <div className="pt-3 border-t border-slate-800">
                          <div className="flex items-center gap-2 text-xs text-slate-400">
                            <Clock className="h-3 w-3" />
                            <span>Built: {formatDate(order.deliverable_metadata.construido_en)}</span>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              ) : (
                <div className="text-center py-6 space-y-3">
                  <Construction className="h-12 w-12 text-cyan-400 mx-auto" />
                  <div>
                    <p className="font-medium text-slate-200">Tu agente aún está en construcción</p>
                    <p className="text-sm text-slate-400 mt-1">
                      Your order is being processed and will be ready soon.
                    </p>
                  </div>
                  <div className="flex items-center justify-center gap-2 text-sm text-slate-400">
                    <Clock className="h-4 w-4" />
                    <span>Progress: {order.progreso}%</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
