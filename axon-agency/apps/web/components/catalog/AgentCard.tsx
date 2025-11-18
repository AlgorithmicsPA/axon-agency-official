"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Megaphone, Code, Phone, Layout, CheckCircle, FileText, 
  LucideIcon 
} from "lucide-react";
import Link from "next/link";

interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  pricing: string;
}

interface AgentCardProps {
  agent: Agent;
}

const iconMap: Record<string, LucideIcon> = {
  megaphone: Megaphone,
  code: Code,
  phone: Phone,
  layout: Layout,
  "check-circle": CheckCircle,
  "file-text": FileText,
};

export function AgentCard({ agent }: AgentCardProps) {
  const Icon = iconMap[agent.icon] || Code;

  return (
    <Link href={`/catalog/${agent.id}`}>
      <Card className="p-6 hover:border-cyan-500/50 transition-all cursor-pointer h-full">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-cyan-500/10 rounded-lg">
            <Icon className="h-6 w-6 text-cyan-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-2">
              <h3 className="font-semibold text-lg">{agent.name}</h3>
              <Badge variant="outline" className="text-xs shrink-0">
                {agent.category}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mb-3">
              {agent.description}
            </p>
            <p className="text-xs text-cyan-400 font-medium">
              {agent.pricing}
            </p>
          </div>
        </div>
      </Card>
    </Link>
  );
}
