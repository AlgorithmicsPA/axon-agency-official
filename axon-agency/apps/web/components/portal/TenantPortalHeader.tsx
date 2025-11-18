"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Building2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface TenantPortalHeaderProps {
  tenantName: string;
  tenantSlug: string;
}

export function TenantPortalHeader({ tenantName, tenantSlug }: TenantPortalHeaderProps) {
  const pathname = usePathname();
  
  const isActive = (path: string) => pathname === path;
  
  return (
    <div className="bg-slate-900 border-b border-slate-800">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Building2 className="h-8 w-8 text-cyan-400" />
            <div>
              <h1 className="text-2xl font-bold text-slate-50">{tenantName}</h1>
              <p className="text-sm text-slate-400">Client Portal</p>
            </div>
          </div>
          <Badge variant="outline" className="text-slate-400 border-slate-700">
            {tenantSlug}
          </Badge>
        </div>
        
        <nav className="flex gap-6">
          <Link
            href={`/portal/${tenantSlug}`}
            className={cn(
              "text-sm font-medium transition-colors hover:text-cyan-400",
              isActive(`/portal/${tenantSlug}`)
                ? "text-cyan-400 border-b-2 border-cyan-400 pb-2"
                : "text-slate-400 pb-2"
            )}
          >
            Dashboard
          </Link>
          <Link
            href={`/portal/${tenantSlug}/orders`}
            className={cn(
              "text-sm font-medium transition-colors hover:text-cyan-400",
              isActive(`/portal/${tenantSlug}/orders`)
                ? "text-cyan-400 border-b-2 border-cyan-400 pb-2"
                : "text-slate-400 pb-2"
            )}
          >
            Orders
          </Link>
        </nav>
      </div>
    </div>
  );
}
