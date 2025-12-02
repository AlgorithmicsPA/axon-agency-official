"use client";

import { useEffect, useState } from "react";
import { useApiClient } from "@/lib/api";
import { Plus, Target, TrendingUp, CheckCircle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useToast } from "@/components/Toast";

export default function CampaignsPage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ name: "", goal: "" });

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const res = await api.get<{ items: any[] }>("/api/campaigns/list");
      setCampaigns(res.items || []);
    } catch (error) {
      console.error("Error fetching campaigns:", error);
    }
  };

  const createCampaign = async () => {
    if (!formData.name || !formData.goal) {
      showToast("Por favor completa todos los campos", "info");
      return;
    }

    try {
      await api.post("/api/campaigns/create", formData);
      setFormData({ name: "", goal: "" });
      setShowModal(false);
      fetchCampaigns();
    } catch (error) {
      console.error("Error creating campaign:", error);
      showToast("Error al crear campaña", "error");
    }
  };

  const statusChartData = [
    { status: 'Activas', count: campaigns.filter(c => c.status === 'active').length },
    { status: 'Borrador', count: campaigns.filter(c => c.status === 'draft').length },
    { status: 'Completadas', count: campaigns.filter(c => c.status === 'completed').length },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Campañas</h1>
          <p className="text-muted-foreground">Gestiona tus campañas de marketing</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-colors"
        >
          <Plus size={20} />
          Nueva Campaña
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Target className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Total Campañas</p>
          </div>
          <p className="text-3xl font-bold">{campaigns.length}</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-green-400" size={20} />
            <p className="text-sm font-medium">Activas</p>
          </div>
          <p className="text-3xl font-bold">{campaigns.filter(c => c.status === 'active').length}</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="text-purple-400" size={20} />
            <p className="text-sm font-medium">Completadas</p>
          </div>
          <p className="text-3xl font-bold">{campaigns.filter(c => c.status === 'completed').length}</p>
        </div>
      </div>

      {campaigns.length > 0 && (
        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-bold mb-4">Distribución por Estado</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={statusChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="status" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="count" fill="#06b6d4" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid gap-4">
        {campaigns.map((campaign) => (
          <div
            key={campaign.id}
            className="bg-card p-6 rounded-lg border border-border hover:border-cyan-500/40 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-xl font-bold mb-2">{campaign.name}</h3>
                <p className="text-muted-foreground mb-3">{campaign.goal}</p>
                <div className="flex items-center gap-3">
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
                  <span className="text-xs text-muted-foreground">
                    Creada: {new Date(campaign.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card p-8 rounded-lg border border-border max-w-md w-full mx-4">
            <h2 className="text-2xl font-bold mb-6">Nueva Campaña</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nombre de la Campaña</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-cyan-500 outline-none"
                  placeholder="Ej: Campaña de Verano 2024"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Objetivo</label>
                <textarea
                  value={formData.goal}
                  onChange={(e) => setFormData({ ...formData, goal: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-cyan-500 outline-none"
                  rows={3}
                  placeholder="Describe el objetivo de la campaña..."
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="flex-1 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={createCampaign}
                className="flex-1 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-colors"
              >
                Crear
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
