import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Megaphone, 
  Phone, 
  Code, 
  Layout, 
  CheckCircle, 
  FileText,
  Bot
} from "lucide-react";

interface Agent {
  id: string;
  name: string;
  icon?: string;
  [key: string]: any;
}

interface Order {
  tipo_producto: string;
  updated_at: string;
  [key: string]: any;
}

interface FactoryAgentsUsageGridProps {
  agents: Agent[];
  orders: Order[];
}

export function FactoryAgentsUsageGrid({ agents, orders }: FactoryAgentsUsageGridProps) {
  const getAgentIcon = (iconName?: string) => {
    const icons: Record<string, any> = {
      megaphone: Megaphone,
      phone: Phone,
      code: Code,
      layout: Layout,
      "check-circle": CheckCircle,
      "file-text": FileText
    };
    return icons[iconName || ""] || Bot;
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

  const agentsWithUsage = agents.map(agent => {
    const agentOrders = orders.filter(order => order.tipo_producto === agent.id);
    const lastOrder = agentOrders.length > 0
      ? agentOrders.sort((a, b) => 
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        )[0]
      : null;

    return {
      ...agent,
      orderCount: agentOrders.length,
      lastOrderAt: lastOrder?.updated_at || null
    };
  }).sort((a, b) => b.orderCount - a.orderCount);

  if (agentsWithUsage.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No agents available</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {agentsWithUsage.map((agent) => {
        const Icon = getAgentIcon(agent.icon);
        const isPopular = agent.orderCount > 5;

        return (
          <Link key={agent.id} href={`/catalog/${agent.id}`}>
            <Card className="hover:bg-accent/50 transition-colors cursor-pointer h-full">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-cyan-500/10">
                      <Icon className="h-5 w-5 text-cyan-400" />
                    </div>
                    <CardTitle className="text-sm font-medium">{agent.name}</CardTitle>
                  </div>
                  {isPopular && (
                    <Badge variant="outline" className="bg-orange-500/10 text-orange-500 border-orange-500/20">
                      🔥 Popular
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Total Orders:</span>
                  <span className="font-semibold text-cyan-400">{agent.orderCount}</span>
                </div>
                {agent.lastOrderAt && (
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Last order:</span>
                    <span>{formatTimeAgo(agent.lastOrderAt)}</span>
                  </div>
                )}
                {!agent.lastOrderAt && agent.orderCount === 0 && (
                  <div className="text-xs text-muted-foreground text-center">
                    No orders yet
                  </div>
                )}
              </CardContent>
            </Card>
          </Link>
        );
      })}
    </div>
  );
}
