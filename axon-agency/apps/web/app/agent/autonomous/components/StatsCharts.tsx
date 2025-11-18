"use client";

import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface GlobalStats {
  total_sessions: number;
  total_improvements_attempted: number;
  total_improvements_succeeded: number;
  overall_success_rate: number;
  success_rate_by_improvement_type: Record<string, number>;
  success_rate_by_mode: Record<string, number>;
  avg_iterations_per_session: number;
}

interface StatsChartsProps {
  stats: GlobalStats;
}

const COLORS = ['#06b6d4', '#8b5cf6', '#f59e0b', '#10b981', '#ef4444'];

export function StatsCharts({ stats }: StatsChartsProps) {
  const improvementTypeData = Object.entries(stats.success_rate_by_improvement_type).map(([type, rate]) => ({
    name: type.replace(/_/g, ' ').toUpperCase(),
    rate: (rate * 100).toFixed(1),
    value: rate * 100
  }));

  const modeData = Object.entries(stats.success_rate_by_mode).map(([mode, rate]) => ({
    name: mode.toUpperCase(),
    rate: (rate * 100).toFixed(1),
    value: rate * 100,
    threshold: mode === 'conservative' ? 80 : mode === 'balanced' ? 60 : mode === 'aggressive' ? 40 : 0
  }));

  const overviewData = [
    { name: 'Exitosas', value: stats.total_improvements_succeeded, color: '#10b981' },
    { name: 'Fallidas', value: stats.total_improvements_attempted - stats.total_improvements_succeeded, color: '#ef4444' }
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-cyan-400">Tasa de Éxito por Tipo de Mejora</h3>
        {improvementTypeData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={improvementTypeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} angle={-45} textAnchor="end" height={100} />
              <YAxis tick={{ fill: '#94a3b8' }} label={{ value: 'Tasa de Éxito (%)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} 
                formatter={(value: any) => [`${value}%`, 'Tasa de Éxito']}
              />
              <Bar dataKey="value" fill="#06b6d4" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            No hay datos suficientes
          </div>
        )}
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-purple-400">Tasa de Éxito por Modo de Operación</h3>
        {modeData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={modeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8' }} />
              <YAxis tick={{ fill: '#94a3b8' }} label={{ value: 'Tasa de Éxito (%)', angle: -90, position: 'insideLeft', fill: '#94a3b8' }} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} 
                formatter={(value: any, name: string) => {
                  if (name === 'threshold') return [`${value}%`, 'Umbral'];
                  return [`${value}%`, 'Tasa de Éxito'];
                }}
              />
              <Legend />
              <Bar dataKey="value" fill="#8b5cf6" name="Tasa de Éxito" radius={[8, 8, 0, 0]} />
              <Bar dataKey="threshold" fill="#64748b" name="Umbral" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            No hay datos suficientes
          </div>
        )}
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-green-400">Distribución de Resultados</h3>
        {overviewData[0].value > 0 || overviewData[1].value > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={overviewData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {overviewData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            No hay datos todavía
          </div>
        )}
      </div>

      <div className="bg-card border border-border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4 text-orange-400">Resumen de Rendimiento</h3>
        <div className="space-y-4">
          <div className="p-4 bg-accent rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-muted-foreground">Tasa de Éxito General</span>
              <span className="text-2xl font-bold text-green-400">
                {(stats.overall_success_rate * 100).toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full transition-all" 
                style={{ width: `${stats.overall_success_rate * 100}%` }}
              />
            </div>
          </div>

          <div className="p-4 bg-accent rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Total de Mejoras</span>
              <span className="text-2xl font-bold text-cyan-400">{stats.total_improvements_attempted}</span>
            </div>
          </div>

          <div className="p-4 bg-accent rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Mejoras Exitosas</span>
              <span className="text-2xl font-bold text-green-400">{stats.total_improvements_succeeded}</span>
            </div>
          </div>

          <div className="p-4 bg-accent rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Promedio Iteraciones/Sesión</span>
              <span className="text-2xl font-bold text-orange-400">{stats.avg_iterations_per_session.toFixed(1)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
