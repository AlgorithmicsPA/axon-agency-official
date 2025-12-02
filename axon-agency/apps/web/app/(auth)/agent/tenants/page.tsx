"use client";

import { useState, useEffect } from "react";
import { useApiClient } from "@/lib/api";
import { AdminOnly } from "@/components/auth/RoleGuard";
import { TenantListTable } from "@/components/tenants/TenantListTable";
import { Button } from "@/components/ui/button";
import { Building, RefreshCw, Loader2, AlertCircle, ShieldX } from "lucide-react";

interface Tenant {
  id: string;
  slug: string;
  name: string;
  business_type: string;
  contact_email: string;
  contact_phone?: string;
  contact_name?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export default function TenantsListPage() {
  const api = useApiClient();
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTenants = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get<any[]>("/api/tenants");
      setTenants(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load tenants");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTenants();
  }, []);

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
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Building className="h-8 w-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-cyan-400">Tenants</h1>
          </div>
          <div className="flex items-center gap-2">
            <Button onClick={fetchTenants} variant="outline" size="sm" disabled={loading}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>
        </div>

        <div className="text-slate-400 text-sm">
          Manage client organizations and their workspaces. Each tenant has its own isolated portal.
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <Loader2 className="animate-spin text-cyan-400" size={48} />
            <p className="text-muted-foreground">Loading tenants...</p>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <AlertCircle className="text-red-400" size={48} />
            <h2 className="text-xl font-semibold text-red-400">{error}</h2>
            <Button onClick={fetchTenants} variant="outline">
              <RefreshCw className="mr-2 h-4 w-4" />
              Retry
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-slate-400">
                Total tenants: <span className="text-cyan-400 font-semibold">{tenants.length}</span>
              </p>
            </div>

            <TenantListTable tenants={tenants} />
          </div>
        )}
      </div>
    </AdminOnly>
  );
}
