import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, FileJson, FileArchive, Download, Calendar } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface DeliverableCardProps {
  orderNumber: string
  tipoProducto: string
  deliverableGenerado: boolean
  deliverableMetadata?: {
    order_number: string
    tipo_producto: string
    qa_status: string | null
    construido_en: string
    archivos: string[]
  }
  deliverableGeneradoEn?: string
}

export function DeliverableCard({
  orderNumber,
  tipoProducto,
  deliverableGenerado,
  deliverableMetadata,
  deliverableGeneradoEn
}: DeliverableCardProps) {
  if (!deliverableGenerado || !deliverableMetadata) {
    return (
      <Card className="border-dashed">
        <CardHeader>
          <CardTitle className="text-sm font-medium">Deliverable</CardTitle>
          <CardDescription>
            No deliverable generated yet. Builder v2 required.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const getFileIcon = (filename: string) => {
    if (filename.endsWith('.md')) return FileText
    if (filename.endsWith('.json')) return FileJson
    if (filename.endsWith('.zip')) return FileArchive
    return FileText
  }

  const sanitizeFilename = (filepath: string): string => {
    if (!filepath) return ''
    const parts = filepath.split('/')
    return parts[parts.length - 1]
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-sm font-medium">Deliverable Package</CardTitle>
            <CardDescription className="flex items-center gap-2 mt-1">
              <Calendar className="h-3 w-3" />
              <span className="text-xs">
                Generated: {new Date(deliverableGeneradoEn || '').toLocaleDateString()}
              </span>
            </CardDescription>
          </div>
          {deliverableMetadata.qa_status && (
            <Badge variant="outline" className="text-xs">
              QA: {deliverableMetadata.qa_status}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <p className="text-xs font-medium text-muted-foreground">Included Files:</p>
          <div className="space-y-1.5">
            {deliverableMetadata.archivos.map((archivo, idx) => {
              const filename = sanitizeFilename(archivo)
              const Icon = getFileIcon(filename)
              return (
                <div
                  key={idx}
                  className="flex items-center gap-2 text-sm p-2 rounded-md bg-muted/50"
                >
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <span className="font-mono text-xs">{filename}</span>
                </div>
              )
            })}
          </div>
        </div>
        
        <Button variant="outline" className="w-full" disabled>
          <Download className="mr-2 h-4 w-4" />
          Download Package (Coming Soon)
        </Button>
      </CardContent>
    </Card>
  )
}
