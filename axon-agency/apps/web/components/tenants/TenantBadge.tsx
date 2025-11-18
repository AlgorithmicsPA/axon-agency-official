import { Badge } from "@/components/ui/badge";

interface TenantBadgeProps {
  businessType: string;
}

const businessTypeConfig: Record<
  string,
  { label: string; className: string }
> = {
  school: {
    label: "School",
    className: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  },
  notary: {
    label: "Notary",
    className: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  },
  delivery: {
    label: "Delivery",
    className: "bg-orange-500/10 text-orange-500 border-orange-500/20",
  },
  health: {
    label: "Health",
    className: "bg-green-500/10 text-green-500 border-green-500/20",
  },
  retail: {
    label: "Retail",
    className: "bg-pink-500/10 text-pink-500 border-pink-500/20",
  },
  general: {
    label: "General",
    className: "bg-slate-500/10 text-slate-500 border-slate-500/20",
  },
};

export function TenantBadge({ businessType }: TenantBadgeProps) {
  const config =
    businessTypeConfig[businessType] || businessTypeConfig.general;

  return (
    <Badge variant="outline" className={config.className}>
      {config.label}
    </Badge>
  );
}
