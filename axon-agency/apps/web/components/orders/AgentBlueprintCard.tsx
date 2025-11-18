import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { FileText, Globe, Zap, MessageSquare, Settings } from "lucide-react"

interface SourceConfig {
  type: string
  value: string
  notes?: string | null
}

interface AgentBlueprint {
  version: string
  agent_type: string
  product_type: string
  sources: SourceConfig[]
  channels: string[]
  capabilities: string[]
  automation_level: string
  client_profile?: Record<string, any> | null
  notes?: string | null
}

interface AgentBlueprintCardProps {
  agentBlueprint?: AgentBlueprint | null
}

export function AgentBlueprintCard({ agentBlueprint }: AgentBlueprintCardProps) {
  if (!agentBlueprint) {
    return (
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Agent Blueprint</CardTitle>
          <CardDescription>
            No blueprint defined for this order yet
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const getSourceIcon = (type: string) => {
    if (type.includes('website') || type.includes('url')) return Globe
    if (type.includes('file') || type.includes('document')) return FileText
    return MessageSquare
  }

  const getAutomationLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'full':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      case 'semi':
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
      case 'manual':
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
      default:
        return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <CardTitle className="text-sm font-medium">Agent Blueprint</CardTitle>
            <CardDescription className="text-xs">
              System specification v{agentBlueprint.version}
            </CardDescription>
          </div>
          <Badge variant="outline" className="text-xs">
            {agentBlueprint.product_type}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Agent Type & Automation Level */}
        <div className="grid grid-cols-2 gap-3">
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Agent Type</p>
            <div className="flex items-center gap-2 p-2 rounded-md bg-muted/50">
              <Settings className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-mono">{agentBlueprint.agent_type}</span>
            </div>
          </div>
          <div className="space-y-1">
            <p className="text-xs font-medium text-muted-foreground">Automation</p>
            <Badge 
              variant="outline" 
              className={`w-full justify-center ${getAutomationLevelColor(agentBlueprint.automation_level)}`}
            >
              <Zap className="h-3 w-3 mr-1" />
              {agentBlueprint.automation_level}
            </Badge>
          </div>
        </div>

        {/* Information Sources */}
        {agentBlueprint.sources.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Information Sources:</p>
            <div className="space-y-1.5">
              {agentBlueprint.sources.map((source, idx) => {
                const Icon = getSourceIcon(source.type)
                return (
                  <div
                    key={idx}
                    className="flex flex-col gap-1 p-2 rounded-md bg-muted/50"
                  >
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                      <Badge variant="outline" className="text-xs">
                        {source.type}
                      </Badge>
                    </div>
                    <p className="text-xs font-mono pl-6 break-all">{source.value}</p>
                    {source.notes && (
                      <p className="text-xs text-muted-foreground pl-6 italic">
                        {source.notes}
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Channels */}
        {agentBlueprint.channels.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Channels:</p>
            <div className="flex flex-wrap gap-1.5">
              {agentBlueprint.channels.map((channel, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs">
                  {channel}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Capabilities */}
        {agentBlueprint.capabilities.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Capabilities:</p>
            <div className="flex flex-wrap gap-1.5">
              {agentBlueprint.capabilities.map((capability, idx) => (
                <Badge key={idx} variant="outline" className="text-xs">
                  {capability}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Client Profile */}
        {agentBlueprint.client_profile && Object.keys(agentBlueprint.client_profile).length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Client Profile:</p>
            <div className="p-2 rounded-md bg-muted/50 space-y-1">
              {Object.entries(agentBlueprint.client_profile).map(([key, value]) => (
                <div key={key} className="flex gap-2 text-xs">
                  <span className="font-medium text-muted-foreground">{key}:</span>
                  <span className="font-mono">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Notes */}
        {agentBlueprint.notes && (
          <div className="space-y-2">
            <p className="text-xs font-medium text-muted-foreground">Notes:</p>
            <p className="text-xs p-2 rounded-md bg-muted/50 text-muted-foreground">
              {agentBlueprint.notes}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
