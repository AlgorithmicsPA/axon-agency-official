"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { Loader2, AlertCircle, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function PortalRedirectPage() {
  const router = useRouter();
  const { user, isAdmin, isTenantUser, tenantSlug, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && isTenantUser && tenantSlug) {
      router.push(`/portal/${tenantSlug}`);
    }
  }, [isLoading, isTenantUser, tenantSlug, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-cyan-400" />
          <p className="text-slate-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (isTenantUser && tenantSlug) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-cyan-400" />
          <p className="text-slate-400">Redirecting to your portal...</p>
        </div>
      </div>
    );
  }

  if (isAdmin && !isTenantUser) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
        <Card className="max-w-md bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-50">
              <ShieldAlert className="h-6 w-6 text-cyan-400" />
              Admin Access
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-slate-300">
              You are an admin. Use the <span className="font-mono text-cyan-400">/agent/*</span> dashboards to manage the system.
            </p>
            <p className="text-sm text-slate-400">
              To view a specific tenant portal, navigate to <span className="font-mono">/portal/&#123;tenantSlug&#125;</span> directly.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <Card className="max-w-md bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-slate-50">
            <AlertCircle className="h-6 w-6 text-red-400" />
            Access Denied
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-300">
            Please log in as a tenant user to access the client portal.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
