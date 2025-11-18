"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { 
  LayoutDashboard, MessageSquare, Megaphone, FileText, Image, 
  MessageCircle, Phone, MessageSquareMore, Bot, CreditCard, 
  Users, UsersRound, BookOpen, Network, Settings, BarChart3, User, Code, Sparkles, TrendingUp, Activity, Store, Factory, Building, Wifi, Package
} from "lucide-react";

const menuItems = [
  { href: "/agent", label: "Super Axon Agent", icon: MessageSquare },
  { href: "/agent/autonomous", label: "Agente Autónomo", icon: Activity },
  { href: "/agent/meta", label: "Meta-Agente", icon: Users },
  { href: "/agent/improve", label: "Mejoras Autónomas", icon: TrendingUp },
  { href: "/catalog", label: "Catálogo de Agentes", icon: Store },
  { href: "/agent/factory", label: "Fábrica de Agentes", icon: Factory, adminOnly: true },
  { href: "/agent/leads", label: "Leads Sales Agent", icon: Users, adminOnly: true },
  { href: "/agent/catalog", label: "Catálogo Autopilots", icon: Package, adminOnly: true },
  { href: "/agent/tenants", label: "Tenants", icon: Building, adminOnly: true },
  { href: "/agent/integrations", label: "Estado de Integraciones", icon: Wifi, adminOnly: true },
  { href: "/playground", label: "Code Playground", icon: Code },
  { href: "/projects/new", label: "Generar Proyecto IA", icon: Sparkles },
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/campaigns", label: "Campañas", icon: Megaphone },
  { href: "/posts", label: "Publicaciones", icon: FileText },
  { href: "/media", label: "Galería de Medios", icon: Image },
  { href: "/conversations", label: "Conversaciones", icon: MessageCircle },
  { href: "/whatsapp", label: "WhatsApp", icon: Phone },
  { href: "/telegram", label: "Telegram", icon: MessageSquareMore },
  { href: "/comments", label: "Comentarios", icon: MessageCircle },
  { href: "/autopilots", label: "Autopilots IA", icon: Bot },
  { href: "/memberships", label: "Membresías", icon: CreditCard },
  { href: "/partners", label: "Asociados", icon: Users },
  { href: "/team", label: "Mi Equipo", icon: UsersRound },
  { href: "/rag", label: "Conocimiento RAG", icon: BookOpen },
  { href: "/networks", label: "Redes Conectadas", icon: Network },
  { href: "/settings", label: "Configuración", icon: Settings },
  { href: "/analytics", label: "Analíticas", icon: BarChart3 },
  { href: "/profile", label: "Mi Perfil", icon: User },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isAdmin } = useAuth();

  return (
    <aside className="w-64 bg-card border-r border-border flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-bold">
          <span className="text-cyan-400">AXON</span> Agency
        </h1>
      </div>
      
      <nav className="flex-1 overflow-y-auto p-4 space-y-1">
        {menuItems.map((item) => {
          if ((item as any).adminOnly && !isAdmin) {
            return null;
          }
          
          const Icon = item.icon;
          const isActive = pathname === item.href;
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                isActive
                  ? "bg-cyan-500/20 text-cyan-400"
                  : "hover:bg-accent text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon size={20} />
              <span className="text-sm">{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
