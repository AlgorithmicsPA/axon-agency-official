import Link from "next/link";
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
import { QAStatusBadge } from "@/components/orders/QAStatusBadge";
import { CheckCircle2, ExternalLink, Minus } from "lucide-react";

interface Order {
  id: string;
  order_number: string;
  tipo_producto: string;
  estado: string;
  qa_status?: "ok" | "warn" | "fail" | null;
  qa_messages?: string[];
  deliverable_generado?: boolean;
  agent_blueprint?: any;
  updated_at: string;
  [key: string]: any;
}

interface FactoryOrdersTableProps {
  orders: Order[];
}

export function FactoryOrdersTable({ orders }: FactoryOrdersTableProps) {
  const recentOrders = [...orders]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 10);

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

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  const extractAgentType = (order: Order): string => {
    if (order.agent_blueprint?.agent_type) {
      return order.agent_blueprint.agent_type;
    }
    return order.tipo_producto.replace(/_/g, ' ');
  };

  return (
    <div className="space-y-4">
      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="min-w-[130px]">Order #</TableHead>
              <TableHead className="min-w-[140px]">Agent Type</TableHead>
              <TableHead className="min-w-[100px]">Estado</TableHead>
              <TableHead className="min-w-[100px]">QA</TableHead>
              <TableHead className="min-w-[80px]">Deliv.</TableHead>
              <TableHead className="min-w-[80px]">Blueprint</TableHead>
              <TableHead className="min-w-[90px]">Updated</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {recentOrders.map((order) => (
              <TableRow key={order.id}>
                <TableCell>
                  <Link 
                    href={`/agent/orders/${order.id}`}
                    className="font-mono text-sm text-cyan-400 hover:text-cyan-300 hover:underline"
                  >
                    {order.order_number}
                  </Link>
                </TableCell>
                <TableCell className="text-sm">
                  {extractAgentType(order)}
                </TableCell>
                <TableCell>
                  <Badge 
                    variant="outline"
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
                  {order.deliverable_generado ? (
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                  ) : (
                    <Minus className="h-4 w-4 text-muted-foreground" />
                  )}
                </TableCell>
                <TableCell>
                  {order.agent_blueprint ? (
                    <CheckCircle2 className="h-4 w-4 text-cyan-500" />
                  ) : (
                    <Minus className="h-4 w-4 text-muted-foreground" />
                  )}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {formatTimeAgo(order.updated_at)}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
      
      <div className="flex justify-center">
        <Link href="/agent/orders">
          <Button variant="outline" size="sm">
            View All Orders
            <ExternalLink className="ml-2 h-3 w-3" />
          </Button>
        </Link>
      </div>
    </div>
  );
}
