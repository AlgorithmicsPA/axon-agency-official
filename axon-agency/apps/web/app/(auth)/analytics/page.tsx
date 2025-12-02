"use client";

import { useEffect, useState } from "react";
import { useApiClient } from "@/lib/api";
import { TrendingUp, Users, MessageSquare, Target, Activity } from "lucide-react";
import { LineChart, Line, BarChart, Bar, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

export default function AnalyticsPage() {
  const api = useApiClient();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [conversations, setConversations] = useState<any[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [campaignsRes, conversationsRes] = await Promise.all([
        api.get<{ items: any[] }>("/api/campaigns/list").catch(() => ({ items: [] })),
        api.get<{ items: any[] }>("/api/conversations/list").catch(() => ({ items: [] })),
      ]);

      setCampaigns(campaignsRes?.items || []);
      setConversations(conversationsRes?.items || []);
    } catch (error) {
      console.error("Error fetching analytics data:", error);
    }
  };

  const engagementData = [
    { day: 'Lun', messages: 45, campaigns: 3 },
    { day: 'Mar', messages: 52, campaigns: 5 },
    { day: 'Mié', messages: 61, campaigns: 4 },
    { day: 'Jue', messages: 58, campaigns: 6 },
    { day: 'Vie', messages: 70, campaigns: 8 },
    { day: 'Sáb', messages: 38, campaigns: 2 },
    { day: 'Dom', messages: 42, campaigns: 3 },
  ];

  const channelData = [
    { name: 'WhatsApp', value: 45, color: '#10b981' },
    { name: 'Telegram', value: 30, color: '#3b82f6' },
    { name: 'Web', value: 25, color: '#06b6d4' },
  ];

  const performanceData = [
    { month: 'Ene', conversions: 120, reach: 450 },
    { month: 'Feb', conversions: 145, reach: 520 },
    { month: 'Mar', conversions: 132, reach: 480 },
    { month: 'Abr', conversions: 168, reach: 590 },
    { month: 'May', conversions: 195, reach: 650 },
    { month: 'Jun', conversions: 210, reach: 720 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Analíticas</h1>
          <p className="text-muted-foreground">Métricas y rendimiento de tu agencia</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Target className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Campañas</p>
          </div>
          <p className="text-3xl font-bold">{campaigns.length}</p>
          <p className="text-xs text-green-400 mt-1">+12% vs mes anterior</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <MessageSquare className="text-purple-400" size={20} />
            <p className="text-sm font-medium">Conversaciones</p>
          </div>
          <p className="text-3xl font-bold">{conversations.length}</p>
          <p className="text-xs text-green-400 mt-1">+8% vs mes anterior</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Users className="text-green-400" size={20} />
            <p className="text-sm font-medium">Alcance Total</p>
          </div>
          <p className="text-3xl font-bold">2.4K</p>
          <p className="text-xs text-green-400 mt-1">+18% vs mes anterior</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-yellow-400" size={20} />
            <p className="text-sm font-medium">Tasa de Conversión</p>
          </div>
          <p className="text-3xl font-bold">8.7%</p>
          <p className="text-xs text-green-400 mt-1">+3.2% vs mes anterior</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <Activity className="text-cyan-400" size={20} />
            Actividad Semanal
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={engagementData}>
              <defs>
                <linearGradient id="colorMessages" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="day" stroke="#888" fontSize={12} />
              <YAxis stroke="#888" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Area type="monotone" dataKey="messages" stroke="#06b6d4" fillOpacity={1} fill="url(#colorMessages)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-bold mb-4">Distribución por Canal</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={channelData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {channelData.map((entry, index) => (
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
      </div>

      <div className="bg-card p-6 rounded-lg border border-border">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <TrendingUp className="text-green-400" size={20} />
          Rendimiento Mensual
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={performanceData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis dataKey="month" stroke="#888" fontSize={12} />
            <YAxis stroke="#888" fontSize={12} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
              labelStyle={{ color: '#fff' }}
            />
            <Line type="monotone" dataKey="conversions" stroke="#10b981" strokeWidth={2} name="Conversiones" />
            <Line type="monotone" dataKey="reach" stroke="#06b6d4" strokeWidth={2} name="Alcance" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-card p-6 rounded-lg border border-border">
        <h2 className="text-lg font-bold mb-4">Top Campañas por Rendimiento</h2>
        <div className="space-y-3">
          {campaigns.slice(0, 5).map((campaign, index) => (
            <div
              key={campaign.id}
              className="flex items-center justify-between p-4 bg-accent rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className="text-2xl font-bold text-cyan-400">#{index + 1}</div>
                <div>
                  <p className="font-medium">{campaign.name}</p>
                  <p className="text-sm text-muted-foreground">{campaign.goal}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-green-400">87%</p>
                <p className="text-xs text-muted-foreground">Engagement</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
