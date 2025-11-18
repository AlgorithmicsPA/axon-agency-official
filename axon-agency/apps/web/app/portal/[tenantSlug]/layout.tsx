"use client";

import { ReactNode } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { TenantPortalHeader } from "@/components/portal/TenantPortalHeader";
import { Loader2, ShieldAlert } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TenantPortalLayout({ children }: { children: ReactNode }) {
  const params = useParams();
  const { isAdmin, isTenantUser, tenantSlug, tenantName, isLoading } = useAuth();
  const requestedSlug = params.tenantSlug as string;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-cyan-400" />
          <p className="text-slate-400">Loading portal...</p>
        </div>
      </div>
    );
  }

  if (!isTenantUser && !isAdmin) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
        <Card className="max-w-md bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-50">
              <ShieldAlert className="h-6 w-6 text-red-400" />
              Access Denied
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-300">
              You do not have permission to access this portal.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isTenantUser && requestedSlug !== tenantSlug) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
        <Card className="max-w-md bg-slate-900 border-slate-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-slate-50">
              <ShieldAlert className="h-6 w-6 text-red-400" />
              Access Denied
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-300">
              You do not have permission to access this tenant portal.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const displayTenantName = tenantName || requestedSlug;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <TenantPortalHeader tenantName={displayTenantName} tenantSlug={requestedSlug} />
      <main className="container mx-auto px-6 py-8">
        {children}
      </main>
    </div>
  );
}
