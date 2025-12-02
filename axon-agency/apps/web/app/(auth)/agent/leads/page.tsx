"use client";

import { useState, useEffect, useMemo } from "react";
import { useApiClient } from "@/lib/api";
import { AdminOnly } from "@/components/auth/RoleGuard";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  RefreshCw,
  Loader2,
  AlertCircle,
  Users,
  UserX,
  Search,
  Building2,
  DollarSign,
  Linkedin,
  Briefcase,
  AlertTriangle
} from "lucide-react";

interface Lead {
  phone: string;
  nombre?: string | null;
  email?: string | null;
  empresa?: string | null;
  sector?: string | null;
  tamano_empresa?: string | null;
  presupuesto_aprox?: string | null;
  linkedin_role?: string | null;
  linkedin_company_size?: string | null;
  linkedin_location?: string | null;
  linkedin_industry?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

interface LeadsResponse {
  leads: Lead[];
  total: number;
}

function LeadsPageContent() {
  const api = useApiClient();
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mongoUnavailable, setMongoUnavailable] = useState(false);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [sectorFilter, setSectorFilter] = useState<string>("all");
  const [limit] = useState(100);
  const [skip] = useState(0);

  const fetchLeads = async () => {
    setLoading(true);
    setError(null);
    setMongoUnavailable(false);

    try {
      const response = await api.get<LeadsResponse>(`/api/leads/list?limit=${limit}&skip=${skip}`);
      setLeads(response.leads);
      setTotal(response.total);
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const error = err as { response?: { status?: number; data?: { detail?: string } } };
        
        if (error.response?.status === 503) {
          setMongoUnavailable(true);
          setError("MongoDB no está configurado. Configura MONGODB_URI para ver leads.");
        } else {
          setError(error.response?.data?.detail || "Error al cargar leads");
        }
      } else {
        setError("Error al cargar leads");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  const filteredLeads = useMemo(() => {
    return leads.filter((lead) => {
      const matchesSearch =
        searchQuery === "" ||
        (lead.nombre?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false) ||
        (lead.email?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false) ||
        (lead.empresa?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false);

      const matchesSector = sectorFilter === "all" || lead.sector === sectorFilter;

      return matchesSearch && matchesSector;
    });
  }, [leads, searchQuery, sectorFilter]);

  const uniqueSectors = useMemo(() => {
    const sectors = new Set<string>();
    leads.forEach((lead) => {
      if (lead.sector) {
        sectors.add(lead.sector);
      }
    });
    return Array.from(sectors).sort();
  }, [leads]);

  const resetFilters = () => {
    setSearchQuery("");
    setSectorFilter("all");
  };

  const formatDate = (dateString?: string | null): string => {
    if (!dateString) return "—";
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <Loader2 className="animate-spin text-cyan-400" size={48} />
        <p className="text-muted-foreground">Cargando leads...</p>
      </div>
    );
  }

  if (mongoUnavailable) {
    return (
      <div className="h-full flex flex-col space-y-6 p-6">
        <div className="flex items-center gap-3">
          <Users className="h-8 w-8 text-cyan-400" />
          <h1 className="text-3xl font-bold text-cyan-400">Leads - WhatsApp Sales Agent</h1>
        </div>

        <div className="flex items-center gap-3 p-4 border border-yellow-500/20 bg-yellow-500/10 rounded-lg">
          <AlertTriangle className="h-6 w-6 text-yellow-500" />
          <div>
            <h3 className="font-semibold text-yellow-500">MongoDB no está configurado</h3>
            <p className="text-sm text-yellow-500/80">
              Configura MONGODB_URI en las variables de entorno para activar el WhatsApp Sales Agent y ver los leads capturados.
            </p>
          </div>
        </div>

        <Button onClick={fetchLeads} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Reintentar
        </Button>
      </div>
    );
  }

  if (error && !mongoUnavailable) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertCircle className="text-red-400" size={48} />
        <h2 className="text-xl font-semibold text-red-400">{error}</h2>
        <Button onClick={fetchLeads} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Reintentar
        </Button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-6 overflow-auto p-6">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <Users className="h-8 w-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-cyan-400">Leads - WhatsApp Sales Agent</h1>
            <Badge className="bg-cyan-500/10 text-cyan-400 border-cyan-500/20">
              {total} Total
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground">
            Leads capturados y cualificados por el agente conversacional
          </p>
        </div>
        <Button onClick={fetchLeads} variant="outline" size="sm">
          <RefreshCw className="mr-2 h-4 w-4" />
          Actualizar
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar por nombre, email o empresa..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-md"
          />
        </div>

        {uniqueSectors.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-muted-foreground">Sector:</label>
            <Select value={sectorFilter} onValueChange={setSectorFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Todos los sectores" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                {uniqueSectors.map((sector) => (
                  <SelectItem key={sector} value={sector}>
                    {sector}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {(searchQuery !== "" || sectorFilter !== "all") && (
          <Button onClick={resetFilters} variant="ghost" size="sm">
            Limpiar Filtros
          </Button>
        )}

        <div className="ml-auto text-sm text-muted-foreground">
          Mostrando <span className="font-semibold text-cyan-400">{filteredLeads.length}</span> de {total} leads
        </div>
      </div>

      {filteredLeads.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 gap-4 border border-dashed rounded-lg">
          <UserX className="h-16 w-16 text-muted-foreground opacity-50" />
          <div className="text-center">
            <h3 className="text-lg font-semibold text-muted-foreground">
              {searchQuery || sectorFilter !== "all" 
                ? "No se encontraron leads con estos filtros" 
                : "No hay leads capturados todavía"}
            </h3>
            <p className="text-sm text-muted-foreground mt-1">
              {searchQuery || sectorFilter !== "all"
                ? "Intenta ajustar tus filtros de búsqueda"
                : "Los leads aparecerán aquí cuando el WhatsApp Sales Agent cualifique contactos"}
            </p>
          </div>
        </div>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="min-w-[160px]">Nombre</TableHead>
                  <TableHead className="min-w-[180px]">Email</TableHead>
                  <TableHead className="min-w-[160px]">Empresa</TableHead>
                  <TableHead className="min-w-[120px]">Sector</TableHead>
                  <TableHead className="min-w-[140px]">Tamaño</TableHead>
                  <TableHead className="min-w-[140px]">Presupuesto</TableHead>
                  <TableHead className="min-w-[120px]">LinkedIn</TableHead>
                  <TableHead className="min-w-[120px]">Fecha</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLeads.map((lead, index) => (
                  <TableRow key={`${lead.phone}-${index}`}>
                    <TableCell className="font-medium">
                      {lead.nombre || (
                        <span className="text-muted-foreground italic">Sin nombre</span>
                      )}
                    </TableCell>
                    <TableCell className="text-sm">
                      {lead.email || (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {lead.empresa ? (
                          <>
                            <Building2 className="h-4 w-4 text-cyan-400" />
                            <span className="text-sm">{lead.empresa}</span>
                          </>
                        ) : (
                          <span className="text-muted-foreground">—</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      {lead.sector ? (
                        <Badge variant="outline" className="bg-purple-500/10 text-purple-400 border-purple-500/20">
                          <Briefcase className="h-3 w-3 mr-1" />
                          {lead.sector}
                        </Badge>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell className="text-sm">
                      {lead.tamano_empresa || (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {lead.presupuesto_aprox ? (
                        <div className="flex items-center gap-1 text-green-400">
                          <DollarSign className="h-4 w-4" />
                          <span className="text-sm">{lead.presupuesto_aprox}</span>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {lead.linkedin_role ? (
                        <Badge className="bg-blue-500/10 text-blue-500 border-blue-500/20">
                          <Linkedin className="h-3 w-3 mr-1" />
                          Enriquecido
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="bg-gray-500/10 text-gray-500 border-gray-500/20">
                          Sin datos
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(lead.created_at)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>
      )}
    </div>
  );
}

export default function LeadsPage() {
  return (
    <AdminOnly>
      <LeadsPageContent />
    </AdminOnly>
  );
}
