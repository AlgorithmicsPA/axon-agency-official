"use client";

import { useState, useEffect, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useApiClient } from "@/lib/api";
import { TenantStatsCard } from "@/components/portal/TenantStatsCard";
import { TenantOrdersTable } from "@/components/portal/TenantOrdersTable";
import { Button } from "@/components/ui/button";
import { Loader2, AlertCircle, Package, TrendingUp, CheckCircle2, XCircle } from "lucide-react";

interface Order {
  id: string;
  order_number: string;
  tipo_producto: string;
  nombre_producto: string;
  estado: string;
  created_at: string;
  updated_at: string;
  deliverable_generado: boolean;
}

export default function TenantDashboardPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApiClient();
  const { tenantName } = useAuth();
  const tenantSlug = params.tenantSlug as string;

  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      setError(null);

      try {
        // Backend automatically filters orders based on JWT token tenant_id
        // Admin users see all orders, tenant users only see their own tenant's orders
        // See: apps/api/app/routers/orders.py::list_orders() for tenant filtering logic
        const response = await api.get("/api/orders?limit=100");
        setOrders(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load orders");
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  const stats = useMemo(() => {
    const total = orders.length;
    const inProgress = orders.filter(o => 
      ['nuevo', 'planificacion', 'construccion', 'qa'].includes(o.estado)
    ).length;
    const ready = orders.filter(o => o.estado === 'listo').length;
    const failed = orders.filter(o => o.estado === 'fallido').length;

    return { total, inProgress, ready, failed };
  }, [orders]);

  const recentOrders = useMemo(() => {
    return [...orders]
      .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
      .slice(0, 10);
  }, [orders]);

  const handleRowClick = (orderId: string) => {
    router.push(`/portal/${tenantSlug}/orders/${orderId}`);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <Loader2 className="h-12 w-12 animate-spin text-cyan-400" />
        <p className="text-slate-400">Loading dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <AlertCircle className="h-12 w-12 text-red-400" />
        <h2 className="text-xl font-semibold text-red-400">{error}</h2>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-50">
          Bienvenido al Portal de {tenantName || tenantSlug}
        </h1>
        <p className="text-slate-400 mt-2">
          Aquí puedes ver tus agentes configurados, órdenes en proceso y entregables listos.
        </p>
      </div>

      {orders.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-96 gap-4 bg-slate-900/50 rounded-lg border border-slate-700">
          <Package className="h-16 w-16 text-slate-600" />
          <div className="text-center space-y-2">
            <h2 className="text-2xl font-semibold text-slate-300">Todavía no hay órdenes</h2>
            <p className="text-slate-400 max-w-md">
              Cuando creemos tu primer agente, aparecerá aquí con su progreso en tiempo real.
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <TenantStatsCard
              title="Total de órdenes"
              value={stats.total}
              icon={Package}
            />
            <TenantStatsCard
              title="En proceso"
              value={stats.inProgress}
              icon={TrendingUp}
              description="Siendo construido por tu agente"
            />
            <TenantStatsCard
              title="Listos"
              value={stats.ready}
              icon={CheckCircle2}
              description="Completados y entregados"
            />
            <TenantStatsCard
              title="Requiere atención"
              value={stats.failed}
              icon={XCircle}
              description="Con problemas"
            />
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-slate-50">Órdenes Recientes</h2>
              <Button
                onClick={() => router.push(`/portal/${tenantSlug}/orders`)}
                variant="outline"
                className="bg-slate-900 border-slate-700 text-slate-200 hover:bg-slate-800"
              >
                Ver todas las órdenes
              </Button>
            </div>

            <TenantOrdersTable
              orders={recentOrders}
              onRowClick={handleRowClick}
            />
          </div>
        </>
      )}
    </div>
  );
}
