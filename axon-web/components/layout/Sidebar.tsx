"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/lib/store";
import {
  LayoutDashboard,
  Server,
  Terminal,
  FolderOpen,
  Workflow,
  Brain,
  MessageSquare,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

const navItems = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/services", icon: Server, label: "Services" },
  { href: "/commands", icon: Terminal, label: "Commands" },
  { href: "/files", icon: FolderOpen, label: "Files" },
  { href: "/flows", icon: Workflow, label: "Flows" },
  { href: "/llm", icon: Brain, label: "LLM" },
  { href: "/chat", icon: MessageSquare, label: "Chat" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarCollapsed, setSidebarCollapsed } = useAppStore();

  return (
    <aside
      className={cn(
        "flex h-screen flex-col border-r border-slate-800 bg-slate-950 transition-all duration-300",
        sidebarCollapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-16 items-center justify-between px-4">
        {!sidebarCollapsed && (
          <h1 className="text-xl font-bold text-glow-cyan">
            Axon <span className="text-cyan-400">Core</span>
          </h1>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="ml-auto"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      <Separator className="bg-slate-800" />

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link key={item.href} href={item.href}>
              <div
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all hover:bg-slate-800",
                  isActive && "bg-slate-800 text-cyan-400 glow-cyan",
                  sidebarCollapsed && "justify-center"
                )}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {!sidebarCollapsed && <span>{item.label}</span>}
              </div>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
