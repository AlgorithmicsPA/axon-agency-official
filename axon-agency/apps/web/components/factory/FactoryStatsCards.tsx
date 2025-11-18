import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Package, 
  FileText, 
  Hammer, 
  CheckCircle2, 
  XCircle, 
  BarChart3 
} from "lucide-react";

interface Order {
  estado: string;
  [key: string]: any;
}

interface FactoryStatsCardsProps {
  orders: Order[];
}

export function FactoryStatsCards({ orders }: FactoryStatsCardsProps) {
  const stats = orders.reduce((acc, order) => {
    const estado = order.estado.toLowerCase();
    acc[estado] = (acc[estado] || 0) + 1;
    acc.total++;
    return acc;
  }, {
    nuevo: 0,
    planificacion: 0,
    construccion: 0,
    listo: 0,
    fallido: 0,
    total: 0
  } as Record<string, number>);

  const statCards = [
    {
      label: "Nuevo",
      value: stats.nuevo,
      icon: Package,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10"
    },
    {
      label: "Planificación",
      value: stats.planificacion,
      icon: FileText,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10"
    },
    {
      label: "Construcción",
      value: stats.construccion,
      icon: Hammer,
      color: "text-cyan-500",
      bgColor: "bg-cyan-500/10"
    },
    {
      label: "Listo",
      value: stats.listo,
      icon: CheckCircle2,
      color: "text-green-500",
      bgColor: "bg-green-500/10"
    },
    {
      label: "Error",
      value: stats.fallido,
      icon: XCircle,
      color: "text-red-500",
      bgColor: "bg-red-500/10"
    },
    {
      label: "Total",
      value: stats.total,
      icon: BarChart3,
      color: "text-cyan-400",
      bgColor: "bg-cyan-500/10"
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {statCards.map((stat) => {
        const Icon = stat.icon;
        return (
          <Card key={stat.label} className={stat.bgColor}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <Icon className={`h-5 w-5 ${stat.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground">{stat.label}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
