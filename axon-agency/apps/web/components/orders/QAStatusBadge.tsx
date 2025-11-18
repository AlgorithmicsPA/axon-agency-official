import { Badge } from "@/components/ui/badge"
import { CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface QAStatusBadgeProps {
  status: "ok" | "warn" | "fail" | null
  messages?: string[]
}

export function QAStatusBadge({ status, messages = [] }: QAStatusBadgeProps) {
  if (!status) {
    return (
      <Badge variant="outline" className="gap-1.5">
        <Clock className="h-3 w-3" />
        <span>QA Pending</span>
      </Badge>
    )
  }

  const statusConfig = {
    ok: {
      icon: CheckCircle2,
      label: "QA Passed",
      variant: "default" as const,
      className: "bg-green-500/10 text-green-500 border-green-500/20"
    },
    warn: {
      icon: AlertTriangle,
      label: "QA Warnings",
      variant: "outline" as const,
      className: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20"
    },
    fail: {
      icon: XCircle,
      label: "QA Failed",
      variant: "destructive" as const,
      className: "bg-red-500/10 text-red-500 border-red-500/20"
    }
  }

  const config = statusConfig[status]
  const Icon = config.icon

  const badge = (
    <Badge variant={config.variant} className={`gap-1.5 ${config.className}`}>
      <Icon className="h-3 w-3" />
      <span>{config.label}</span>
    </Badge>
  )

  if (messages.length === 0) {
    return badge
  }

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>{badge}</TooltipTrigger>
        <TooltipContent className="max-w-md">
          <div className="space-y-1">
            <p className="font-semibold text-sm">QA Messages:</p>
            <ul className="list-disc list-inside text-xs space-y-0.5">
              {messages.map((msg, idx) => (
                <li key={idx}>{msg}</li>
              ))}
            </ul>
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
