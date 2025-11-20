"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { useApiClient } from "@/lib/api";
import { QAStatusBadge } from "@/components/orders/QAStatusBadge";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  RefreshCw, 
  Loader2, 
  AlertCircle, 
  Package,
  ExternalLink
} from "lucide-react";

interface OrderListItem {
  id: string;
  order_number: string;
  tipo_producto: string;
  nombre_producto: string;
  estado: string;
  progreso: number;
  prioridad: string;
  tags: string[];
  asignado_a: string | null;
  created_at: string;
  updated_at: string;
  qa_status?: "ok" | "warn" | "fail" | null;
  qa_messages?: string[];
}

export default function OrdersListPage() {
  const api = useApiClient();
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [estadoFilter, setEstadoFilter] = useState<string>("all");
  const [qaFilter, setQaFilter] = useState<string>("all");

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await api.get("/api/orders");
      setOrders(response.data);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || "Failed to load orders");
      } else {
        setError("Failed to load orders");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const filteredOrders = useMemo(() => {
    return orders.filter((order) => {
      const matchesEstado = estadoFilter === "all" || order.estado === estadoFilter;
      
      let matchesQa = true;
      if (qaFilter !== "all") {
        if (qaFilter === "pending") {
          matchesQa = !order.qa_status;
        } else {
          matchesQa = order.qa_status === qaFilter;
        }
      }
      
      return matchesEstado && matchesQa;
    });
  }, [orders, estadoFilter, qaFilter]);

  const resetFilters = () => {
    setEstadoFilter("all");
    setQaFilter("all");
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

  const getPrioridadColor = (prioridad: string): string => {
    const colors: Record<string, string> = {
      baja: "bg-gray-500/10 text-gray-400 border-gray-500/20",
      normal: "bg-blue-500/10 text-blue-400 border-blue-500/20",
      alta: "bg-orange-500/10 text-orange-400 border-orange-500/20",
      urgente: "bg-red-500/10 text-red-400 border-red-500/20"
    };
    return colors[prioridad] || colors.normal;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <Loader2 className="animate-spin text-cyan-400" size={48} />
        <p className="text-muted-foreground">Loading orders...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertCircle className="text-red-400" size={48} />
        <h2 className="text-xl font-semibold text-red-400">{error}</h2>
        <Button onClick={fetchOrders} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-6 overflow-auto p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Package className="h-8 w-8 text-cyan-400" />
          <h1 className="text-3xl font-bold text-cyan-400">Orders Factory</h1>
        </div>
        <Button onClick={fetchOrders} variant="outline" size="sm">
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-muted-foreground">Estado:</label>
          <Select value={estadoFilter} onValueChange={setEstadoFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="nuevo">Nuevo</SelectItem>
              <SelectItem value="planificacion">Planificación</SelectItem>
              <SelectItem value="construccion">Construcción</SelectItem>
              <SelectItem value="qa">QA</SelectItem>
              <SelectItem value="listo">Listo</SelectItem>
              <SelectItem value="entregado">Entregado</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-muted-foreground">QA Status:</label>
          <Select value={qaFilter} onValueChange={setQaFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Filter by QA" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="ok">OK</SelectItem>
              <SelectItem value="warn">Warning</SelectItem>
              <SelectItem value="fail">Failed</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {(estadoFilter !== "all" || qaFilter !== "all") && (
          <Button onClick={resetFilters} variant="ghost" size="sm">
            Reset Filters
          </Button>
        )}

        <div className="ml-auto text-sm text-muted-foreground">
          Showing <span className="font-semibold text-cyan-400">{filteredOrders.length}</span> of {orders.length} orders
        </div>
      </div>

      {filteredOrders.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 gap-4 border border-dashed rounded-lg">
          <Package className="h-16 w-16 text-muted-foreground opacity-50" />
          <div className="text-center">
            <h3 className="text-lg font-semibold text-muted-foreground">No orders found</h3>
            <p className="text-sm text-muted-foreground mt-1">
              {estadoFilter !== "all" || qaFilter !== "all" 
                ? "Try adjusting your filters" 
                : "Create your first order to get started"}
            </p>
          </div>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="min-w-[140px]">Order Number</TableHead>
                  <TableHead className="min-w-[160px]">Tipo Producto</TableHead>
                  <TableHead className="min-w-[200px]">Nombre Producto</TableHead>
                  <TableHead className="min-w-[120px]">Estado</TableHead>
                  <TableHead className="min-w-[140px]">QA Status</TableHead>
                  <TableHead className="min-w-[150px]">Progreso</TableHead>
                  <TableHead className="min-w-[100px]">Prioridad</TableHead>
                  <TableHead className="min-w-[140px]">Asignado A</TableHead>
                  <TableHead className="min-w-[120px] text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOrders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell>
                      <Link 
                        href={`/agent/orders/${order.id}`}
                        className="font-mono text-sm text-cyan-400 hover:text-cyan-300 hover:underline"
                      >
                        {order.order_number}
                      </Link>
                    </TableCell>
                    <TableCell className="text-sm">{order.tipo_producto}</TableCell>
                    <TableCell className="font-medium">{order.nombre_producto}</TableCell>
                    <TableCell>
                      <Badge 
                        variant={getEstadoBadgeVariant(order.estado)}
                        className={getEstadoBadgeColor(order.estado)}
                      >
                        {order.estado}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <QAStatusBadge 
                        status={order.qa_status || null}
                        messages={order.qa_messages || []}
                      />
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 bg-accent rounded-full h-2 overflow-hidden min-w-[80px]">
                          <div 
                            className="bg-cyan-500 h-full transition-all duration-300"
                            style={{ width: `${order.progreso}%` }}
                          />
                        </div>
                        <span className="text-sm font-semibold text-cyan-400 min-w-[40px]">
                          {order.progreso}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline"
                        className={getPrioridadColor(order.prioridad)}
                      >
                        {order.prioridad}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {order.asignado_a || "—"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/agent/orders/${order.id}`}>
                        <Button variant="ghost" size="sm">
                          View Details
                          <ExternalLink className="ml-2 h-3 w-3" />
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}
    </div>
  );
}
