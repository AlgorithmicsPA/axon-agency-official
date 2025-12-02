"use client";

import { useEffect, useState } from "react";
import { useApiClient } from "@/lib/api";
import { Activity, Cpu, HardDrive, TrendingUp, MessageSquare, Target } from "lucide-react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

export default function Dashboard() {
  const api = useApiClient();
  const [metrics, setMetrics] = useState<any>(null);
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [conversations, setConversations] = useState<any[]>([]);
  const [metricsHistory, setMetricsHistory] = useState<any[]>([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // ApiClient devuelve directamente el tipo T, no un objeto con 'data'
      const [metricsRes, campaignsRes, conversationsRes] = await Promise.all([
        api.get("/api/metrics").catch(() => null),
        api.get<{ items: any[] }>("/api/campaigns/list").catch(() => ({ items: [] })),
        api.get<{ items: any[] }>("/api/conversations/list").catch(() => ({ items: [] })),
      ]);

      if (metricsRes) {
        setMetrics(metricsRes);
        setMetricsHistory(prev => {
          const newHistory = [...prev, {
            time: new Date().toLocaleTimeString(),
            cpu: metricsRes.cpu?.percent || 0,
            memory: metricsRes.memory?.percent || 0,
            disk: metricsRes.disk?.percent || 0
          }];
          return newHistory.slice(-10);
        });
      }

      setCampaigns(campaignsRes?.items || []);
      setConversations(conversationsRes?.items || []);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    }
  };

  const campaignStatusData = [
    { name: 'Activas', value: campaigns.filter(c => c.status === 'active').length, color: '#06b6d4' },
    { name: 'Borrador', value: campaigns.filter(c => c.status === 'draft').length, color: '#8b5cf6' },
    { name: 'Completadas', value: campaigns.filter(c => c.status === 'completed').length, color: '#10b981' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-cyan-400">Dashboard</h1>
        <p className="text-muted-foreground">Panel de control de AXON Agency</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {metrics && (
          <>
            <div className="bg-card p-6 rounded-lg border border-cyan-500/20 hover:border-cyan-500/40 transition-colors">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-cyan-500/10 rounded-lg">
                  <Cpu className="text-cyan-400" size={24} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">CPU</p>
                  <p className="text-2xl font-bold">{metrics.cpu.percent.toFixed(1)}%</p>
                </div>
              </div>
            </div>

            <div className="bg-card p-6 rounded-lg border border-purple-500/20 hover:border-purple-500/40 transition-colors">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/10 rounded-lg">
                  <Activity className="text-purple-400" size={24} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Memoria</p>
                  <p className="text-2xl font-bold">{metrics.memory.percent.toFixed(1)}%</p>
                </div>
              </div>
            </div>

            <div className="bg-card p-6 rounded-lg border border-cyan-500/20 hover:border-cyan-500/40 transition-colors">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-cyan-500/10 rounded-lg">
                  <HardDrive className="text-cyan-400" size={24} />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Disco</p>
                  <p className="text-2xl font-bold">{metrics.disk.percent.toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Target className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Campañas Totales</p>
          </div>
          <p className="text-3xl font-bold">{campaigns.length}</p>
          <p className="text-xs text-muted-foreground mt-1">
            {campaigns.filter(c => c.status === 'active').length} activas
          </p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <MessageSquare className="text-purple-400" size={20} />
            <p className="text-sm font-medium">Conversaciones</p>
          </div>
          <p className="text-3xl font-bold">{conversations.length}</p>
          <p className="text-xs text-muted-foreground mt-1">Últimas 24h</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-green-400" size={20} />
            <p className="text-sm font-medium">Engagement</p>
          </div>
          <p className="text-3xl font-bold">87%</p>
          <p className="text-xs text-muted-foreground mt-1">+12% vs ayer</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {metricsHistory.length > 0 && (
          <div className="bg-card p-6 rounded-lg border border-border">
            <h2 className="text-lg font-bold mb-4">Métricas del Sistema (Tiempo Real)</h2>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={metricsHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="time" stroke="#888" fontSize={12} />
                <YAxis stroke="#888" fontSize={12} domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                  labelStyle={{ color: '#fff' }}
                />
                <Line type="monotone" dataKey="cpu" stroke="#06b6d4" strokeWidth={2} name="CPU %" />
                <Line type="monotone" dataKey="memory" stroke="#8b5cf6" strokeWidth={2} name="Memoria %" />
                <Line type="monotone" dataKey="disk" stroke="#10b981" strokeWidth={2} name="Disco %" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {campaigns.length > 0 && (
          <div className="bg-card p-6 rounded-lg border border-border">
            <h2 className="text-lg font-bold mb-4">Estado de Campañas</h2>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={campaignStatusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {campaignStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                  labelStyle={{ color: '#fff' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {campaigns.length > 0 && (
        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-bold mb-4">Campañas Recientes</h2>
          <div className="space-y-3">
            {campaigns.slice(0, 5).map((campaign) => (
              <div
                key={campaign.id}
                className="flex items-center justify-between p-4 bg-accent rounded-lg hover:bg-accent/80 transition-colors"
              >
                <div>
                  <p className="font-medium">{campaign.name}</p>
                  <p className="text-sm text-muted-foreground">{campaign.goal}</p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    campaign.status === 'active'
                      ? 'bg-cyan-500/20 text-cyan-400'
                      : campaign.status === 'completed'
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-purple-500/20 text-purple-400'
                  }`}
                >
                  {campaign.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
