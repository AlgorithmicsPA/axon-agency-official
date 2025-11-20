"use client";

import { useState, useEffect, useMemo } from "react";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useApiClient } from "@/lib/api";
import { TenantOrdersTable } from "@/components/portal/TenantOrdersTable";
import { Loader2, AlertCircle, Package } from "lucide-react";

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

export default function TenantOrdersListPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApiClient();
  const { tenantName } = useAuth();
  const tenantSlug = params.tenantSlug as string;

  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [estadoFilter, setEstadoFilter] = useState<string>("all");

  useEffect(() => {
    const fetchOrders = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await api.get("/api/orders?limit=200");
        setOrders(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load orders");
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  const filteredOrders = useMemo(() => {
    if (estadoFilter === "all") {
      return orders;
    }
    
    if (estadoFilter === "listo") {
      return orders.filter(o => o.estado === "listo");
    }
    
    if (estadoFilter === "progress") {
      return orders.filter(o => 
        ['nuevo', 'planificacion', 'construccion', 'qa'].includes(o.estado)
      );
    }
    
    if (estadoFilter === "fallido") {
      return orders.filter(o => o.estado === "fallido");
    }
    
    return orders;
  }, [orders, estadoFilter]);

  const handleRowClick = (orderId: string) => {
    router.push(`/portal/${tenantSlug}/orders/${orderId}`);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <Loader2 className="h-12 w-12 animate-spin text-cyan-400" />
        <p className="text-slate-400">Loading orders...</p>
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
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Package className="h-8 w-8 text-cyan-400" />
        <div>
          <h1 className="text-3xl font-bold text-slate-50">Órdenes de {tenantName || tenantSlug}</h1>
          <p className="text-slate-400 mt-1">
            {filteredOrders.length} of {orders.length} orders
          </p>
        </div>
      </div>

      <TenantOrdersTable
        orders={filteredOrders}
        onRowClick={handleRowClick}
        showFilters
        estadoFilter={estadoFilter}
        onEstadoFilterChange={setEstadoFilter}
      />
    </div>
  );
}
