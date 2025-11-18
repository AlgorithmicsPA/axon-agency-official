"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { Server, Play, Square, RotateCw, Search } from "lucide-react";
import type { ServiceStatus } from "@/lib/types";

export default function Services() {
  const [search, setSearch] = useState("");
  const api = useApiClient();
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: services, isLoading } = useQuery({
    queryKey: ["services"],
    queryFn: async () => {
      const { data } = await api.post<{ services: ServiceStatus[] }>("/api/services/list", {});
      return data.services;
    },
  });

  const controlMutation = useMutation({
    mutationFn: async ({ name, action }: { name: string; action: string }) => {
      const { data } = await api.post("/api/services/control", { name, action });
      return data;
    },
    onSuccess: (_, variables) => {
      toast({
        title: "Action successful",
        description: `${variables.action} executed on ${variables.name}`,
      });
      queryClient.invalidateQueries({ queryKey: ["services"] });
    },
    onError: (error: any) => {
      toast({
        variant: "destructive",
        title: "Action failed",
        description: error.response?.data?.detail || "Failed to execute action",
      });
    },
  });

  const filteredServices =
    services?.filter((s) => s.name.toLowerCase().includes(search.toLowerCase())) || [];

  const getStatusBadge = (status: string) => {
    const isActive = status.toLowerCase().includes("active") || status.toLowerCase().includes("running");
    return (
      <Badge variant={isActive ? "default" : "outline"} className={isActive ? "bg-green-500" : ""}>
        {status}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-glow-cyan flex items-center gap-3">
          <Server className="h-8 w-8" />
          Services
        </h1>
        <p className="text-slate-400 mt-2">Manage systemd and Docker services</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Service List</CardTitle>
          <div className="pt-4">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search services..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-slate-400">Loading services...</div>
          ) : (
            <div className="space-y-2">
              {filteredServices.map((service) => (
                <div
                  key={service.name}
                  className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 p-4"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <span className="font-semibold">{service.name}</span>
                      {getStatusBadge(service.status)}
                      {service.type && (
                        <Badge variant="outline" className="text-xs">
                          {service.type}
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => controlMutation.mutate({ name: service.name, action: "start" })}
                      disabled={controlMutation.isPending}
                    >
                      <Play className="h-3 w-3 mr-1" />
                      Start
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => controlMutation.mutate({ name: service.name, action: "stop" })}
                      disabled={controlMutation.isPending}
                    >
                      <Square className="h-3 w-3 mr-1" />
                      Stop
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => controlMutation.mutate({ name: service.name, action: "restart" })}
                      disabled={controlMutation.isPending}
                    >
                      <RotateCw className="h-3 w-3 mr-1" />
                      Restart
                    </Button>
                  </div>
                </div>
              ))}

              {filteredServices.length === 0 && (
                <div className="text-center py-8 text-slate-400">
                  {search ? "No services match your search" : "No services available"}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
