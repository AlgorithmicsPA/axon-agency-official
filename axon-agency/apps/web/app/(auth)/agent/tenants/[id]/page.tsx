"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useApiClient } from "@/lib/api";
import { AdminOnly } from "@/components/auth/RoleGuard";
import { TenantForm } from "@/components/tenants/TenantForm";
import { TenantBadge } from "@/components/tenants/TenantBadge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Building,
  ExternalLink,
  Loader2,
  AlertCircle,
  ArrowLeft,
  ShieldX,
  Package,
} from "lucide-react";

interface Tenant {
  id: string;
  slug: string;
  name: string;
  business_type: string;
  contact_email: string;
  contact_phone?: string;
  contact_name?: string;
  branding?: {
    primary_color?: string;
  };
  active: boolean;
  created_at: string;
  updated_at: string;
  notes: string;
}

interface OrderStats {
  total: number;
  lastOrderDate?: string;
}

export default function TenantDetailPage() {
  const params = useParams();
  const router = useRouter();
  const api = useApiClient();
  const tenantId = params.id as string;

  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [orderStats, setOrderStats] = useState<OrderStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTenantData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [tenantRes, ordersRes] = await Promise.all([
        api.get(`/api/tenants/${tenantId}`),
        api.get(`/api/orders?tenant_id=${tenantId}`),
      ]);

      setTenant(tenantRes.data);

      const orders = ordersRes.data;
      const stats: OrderStats = {
        total: orders.length,
      };

      if (orders.length > 0) {
        const sortedOrders = [...orders].sort(
          (a, b) =>
            new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        );
        stats.lastOrderDate = sortedOrders[0].updated_at;
      }

      setOrderStats(stats);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load tenant");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTenantData();
  }, [tenantId]);

  const unauthorizedFallback = (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <ShieldX className="h-16 w-16 text-red-400" />
      <h2 className="text-2xl font-semibold text-red-400">Access Denied</h2>
      <p className="text-muted-foreground">
        This page is only accessible to administrators.
      </p>
    </div>
  );

  return (
    <AdminOnly fallback={unauthorizedFallback}>
      <div className="h-full flex flex-col space-y-6 overflow-auto p-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="animate-spin text-cyan-400" size={48} />
            <p className="text-muted-foreground">Loading tenant...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <AlertCircle className="text-red-400" size={48} />
            <h2 className="text-xl font-semibold text-red-400">{error}</h2>
            <Button onClick={fetchTenantData} variant="outline">
              Retry
            </Button>
          </div>
        ) : tenant ? (
          <>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Button
                  asChild
                  variant="outline"
                  size="icon"
                  className="border-slate-700"
                >
                  <Link href="/agent/tenants">
                    <ArrowLeft className="h-4 w-4" />
                  </Link>
                </Button>
                <Building className="h-8 w-8 text-cyan-400" />
                <div>
                  <h1 className="text-3xl font-bold text-cyan-400">
                    {tenant.name}
                  </h1>
                  <div className="flex items-center gap-2 mt-1">
                    <TenantBadge businessType={tenant.business_type} />
                    <span className="text-sm text-slate-500 font-mono">
                      {tenant.slug}
                    </span>
                  </div>
                </div>
              </div>
              <Button
                asChild
                variant="outline"
                className="border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/10"
              >
                <Link
                  href={`/portal/${tenant.slug}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <ExternalLink className="mr-2 h-4 w-4" />
                  View Portal
                </Link>
              </Button>
            </div>

            {orderStats && (
              <Card className="bg-slate-900 border-slate-800">
                <CardHeader>
                  <CardTitle className="text-slate-200 flex items-center gap-2">
                    <Package className="h-5 w-5 text-cyan-400" />
                    Order Summary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-slate-400">Total Orders</p>
                      <p className="text-2xl font-bold text-cyan-400">
                        {orderStats.total}
                      </p>
                    </div>
                    {orderStats.lastOrderDate && (
                      <div>
                        <p className="text-sm text-slate-400">Last Order</p>
                        <p className="text-lg text-slate-200">
                          {new Date(orderStats.lastOrderDate).toLocaleDateString()}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            <TenantForm tenant={tenant} onUpdate={fetchTenantData} />
          </>
        ) : null}
      </div>
    </AdminOnly>
  );
}
