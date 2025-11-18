import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface TenantStatsCardProps {
  title: string;
  value: number | string;
  icon?: LucideIcon;
  description?: string;
}

export function TenantStatsCard({ title, value, icon: Icon, description }: TenantStatsCardProps) {
  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-slate-200">{title}</CardTitle>
        {Icon && <Icon className="h-4 w-4 text-cyan-400" />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-slate-50">{value}</div>
        {description && (
          <p className="text-xs text-slate-400 mt-1">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}
