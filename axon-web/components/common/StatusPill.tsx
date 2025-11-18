"use client";

import { Badge } from "@/components/ui/badge";
import type { WSStatus } from "@/lib/types";
import { Circle } from "lucide-react";

interface StatusPillProps {
  status: WSStatus;
}

export function StatusPill({ status }: StatusPillProps) {
  const statusConfig = {
    connected: { label: "Connected", color: "text-green-400", bg: "bg-green-400/20" },
    connecting: { label: "Connecting", color: "text-yellow-400", bg: "bg-yellow-400/20" },
    disconnected: { label: "Disconnected", color: "text-gray-400", bg: "bg-gray-400/20" },
    error: { label: "Error", color: "text-red-400", bg: "bg-red-400/20" },
  };

  const config = statusConfig[status];

  return (
    <Badge variant="outline" className={`${config.bg} border-0 gap-2`}>
      <Circle className={`h-2 w-2 fill-current ${config.color}`} />
      <span className={config.color}>{config.label}</span>
    </Badge>
  );
}
