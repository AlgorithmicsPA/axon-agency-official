"use client";

import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Check, X } from "lucide-react";

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

interface TenantOrdersTableProps {
  orders: Order[];
  onRowClick: (orderId: string) => void;
  showFilters?: boolean;
  estadoFilter?: string;
  onEstadoFilterChange?: (value: string) => void;
}

export function TenantOrdersTable({ 
  orders, 
  onRowClick, 
  showFilters = false,
  estadoFilter = "all",
  onEstadoFilterChange
}: TenantOrdersTableProps) {
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
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="space-y-4">
      {showFilters && onEstadoFilterChange && (
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-slate-400">Filter by Estado:</label>
          <Select value={estadoFilter} onValueChange={onEstadoFilterChange}>
            <SelectTrigger className="w-[180px] bg-slate-900 border-slate-800">
              <SelectValue placeholder="All States" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="listo">Listo</SelectItem>
              <SelectItem value="progress">En Progreso</SelectItem>
              <SelectItem value="fallido">Fallido</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      <div className="border border-slate-800 rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow className="border-slate-800 hover:bg-slate-900/50">
              <TableHead className="text-slate-400">Order #</TableHead>
              <TableHead className="text-slate-400">Product Name</TableHead>
              <TableHead className="text-slate-400">Estado</TableHead>
              <TableHead className="text-slate-400">Last Updated</TableHead>
              <TableHead className="text-slate-400 text-center">Deliverable</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {orders.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center text-slate-400 py-8">
                  No orders found
                </TableCell>
              </TableRow>
            ) : (
              orders.map((order) => (
                <TableRow
                  key={order.id}
                  className="border-slate-800 hover:bg-slate-900/50 cursor-pointer"
                  onClick={() => onRowClick(order.id)}
                >
                  <TableCell className="font-mono text-sm text-cyan-400">
                    {order.order_number}
                  </TableCell>
                  <TableCell className="font-medium text-slate-200">
                    {order.nombre_producto}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getEstadoBadgeColor(order.estado)}>
                      {order.estado}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm text-slate-400">
                    {formatDate(order.updated_at)}
                  </TableCell>
                  <TableCell className="text-center">
                    {order.deliverable_generado ? (
                      <Check className="h-5 w-5 text-green-500 inline-block" />
                    ) : (
                      <span className="text-sm text-slate-500">Pendiente</span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
