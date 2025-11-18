"use client";

import { useState, useEffect } from "react";
import { useApiClient } from "@/lib/api";
import { useToast } from "@/components/Toast";
import { AdminOnly } from "@/components/auth/RoleGuard";
import { FactoryStatsCards } from "@/components/factory/FactoryStatsCards";
import { FactoryOrdersTable } from "@/components/factory/FactoryOrdersTable";
import { FactoryAgentsUsageGrid } from "@/components/factory/FactoryAgentsUsageGrid";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Factory, RefreshCw, Loader2, AlertCircle, ShieldX, Sparkles } from "lucide-react";

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

interface Agent {
  id: string;
  name: string;
  icon?: string;
  [key: string]: any;
}

export default function FactoryDashboardPage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const [orders, setOrders] = useState<Order[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [ordersRes, agentsRes] = await Promise.all([
        api.get("/api/orders?limit=1000"),
        api.get("/api/catalog/agents")
      ]);
      
      setOrders(ordersRes.data);
      setAgents(agentsRes.data.agents || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSeedDemo = async () => {
    setSeeding(true);
    try {
      const response = await api.post("/api/admin/seed-demo");
      showToast(
        `Demo data created: ${response.data.tenants_created} tenants, ${response.data.orders_created} orders`,
        "success"
      );
      await fetchData();
    } catch (err: any) {
      showToast(
        err.response?.data?.detail || "Failed to create demo data",
        "error"
      );
    } finally {
      setSeeding(false);
    }
  };

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
          <div className="flex items-center gap-3">
            <Factory className="h-8 w-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-cyan-400">Agent Factory</h1>
          </div>
          <Button onClick={fetchData} variant="outline" size="sm" disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="animate-spin text-cyan-400" size={48} />
            <p className="text-muted-foreground">Loading factory data...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <AlertCircle className="text-red-400" size={48} />
            <h2 className="text-xl font-semibold text-red-400">{error}</h2>
            <Button onClick={fetchData} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </div>
        ) : (
          <>
            <section>
              <h2 className="text-lg font-semibold mb-4 text-muted-foreground">
                🎭 Demo Data Seeder
              </h2>
              <Card className="border-yellow-500/50 bg-yellow-500/5">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-yellow-400" />
                    Crear Datos Demo
                  </CardTitle>
                  <CardDescription>
                    Solo uso interno. Crea tenants y órdenes de demostración para testing.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={handleSeedDemo} 
                    disabled={seeding}
                    variant="outline"
                    className="border-yellow-500/50 hover:bg-yellow-500/10"
                  >
                    {seeding ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Creando datos demo...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Seed Demo Data
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </section>

            <section>
              <h2 className="text-lg font-semibold mb-4 text-muted-foreground">
                📊 Factory Stats
              </h2>
              <FactoryStatsCards orders={orders} />
            </section>

            <section>
              <h2 className="text-lg font-semibold mb-4 text-muted-foreground">
                📦 Recent Orders
              </h2>
              <FactoryOrdersTable orders={orders} />
            </section>

            <section>
              <h2 className="text-lg font-semibold mb-4 text-muted-foreground">
                🤖 Agent Catalog Usage
              </h2>
              <FactoryAgentsUsageGrid agents={agents} orders={orders} />
            </section>
          </>
        )}
      </div>
    </AdminOnly>
  );
}
