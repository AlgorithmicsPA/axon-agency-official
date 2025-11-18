"use client";

import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api";
import { useMetrics } from "@/hooks/useMetrics";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Cpu, HardDrive, Clock, Thermometer, Zap } from "lucide-react";
import type { HealthStatus } from "@/lib/types";

export default function Dashboard() {
  const api = useApiClient();
  
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const { data } = await api.get<HealthStatus>("/api/health");
      return data;
    },
    refetchInterval: 5000,
  });

  const { data: metrics } = useMetrics();

  const formatBytes = (bytes: number) => {
    const gb = bytes / (1024 ** 3);
    return `${gb.toFixed(2)} GB`;
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${mins}m`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-glow-cyan">Dashboard</h1>
        <p className="text-slate-400 mt-2">System metrics and health overview</p>
      </div>

      {health && (
        <Card className="glow-cyan">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-400" />
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-slate-400">Status</p>
                <p className="text-xl font-semibold text-green-400">{health.status}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Version</p>
                <p className="text-xl font-semibold">{health.version}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Timestamp</p>
                <p className="text-xl font-semibold font-mono text-xs">
                  {new Date(health.timestamp).toLocaleString()}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {metrics && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Cpu className="h-4 w-4 text-cyan-400" />
                CPU Usage
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-cyan-400">{metrics.cpu.toFixed(1)}%</div>
              <div className="mt-2 h-2 rounded-full bg-slate-800">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500"
                  style={{ width: `${metrics.cpu}%` }}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Activity className="h-4 w-4 text-fuchsia-400" />
                RAM Usage
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-fuchsia-400">
                {metrics.ram.percent.toFixed(1)}%
              </div>
              <p className="text-sm text-slate-400 mt-2">
                {formatBytes(metrics.ram.used)} / {formatBytes(metrics.ram.total)}
              </p>
              <div className="mt-2 h-2 rounded-full bg-slate-800">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-fuchsia-500 to-pink-500"
                  style={{ width: `${metrics.ram.percent}%` }}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <HardDrive className="h-4 w-4 text-emerald-400" />
                Disk Usage
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-emerald-400">
                {metrics.disk.percent.toFixed(1)}%
              </div>
              <p className="text-sm text-slate-400 mt-2">
                {formatBytes(metrics.disk.used)} / {formatBytes(metrics.disk.total)}
              </p>
              <div className="mt-2 h-2 rounded-full bg-slate-800">
                <div
                  className="h-2 rounded-full bg-gradient-to-r from-emerald-500 to-green-500"
                  style={{ width: `${metrics.disk.percent}%` }}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">
                <Clock className="h-4 w-4 text-blue-400" />
                Uptime
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">{formatUptime(metrics.uptime)}</div>
            </CardContent>
          </Card>

          {metrics.gpu && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Zap className="h-4 w-4 text-yellow-400" />
                    GPU Utilization
                  </CardTitle>
                  <CardDescription>{metrics.gpu.name}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-yellow-400">
                    {metrics.gpu.utilization.toFixed(1)}%
                  </div>
                  <p className="text-sm text-slate-400 mt-2">
                    {formatBytes(metrics.gpu.memory_used)} / {formatBytes(metrics.gpu.memory_total)}
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                    <Thermometer className="h-4 w-4 text-orange-400" />
                    GPU Temperature
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold text-orange-400">{metrics.gpu.temp}°C</div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      )}
    </div>
  );
}
