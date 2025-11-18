"use client";

import { useAppStore } from "@/lib/store";
import { StatusPill } from "@/components/common/StatusPill";

export function Topbar() {
  const { wsStatus } = useAppStore();

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-950 px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-sm font-medium text-slate-400">System Control Panel</h2>
      </div>

      <div className="flex items-center gap-4">
        <StatusPill status={wsStatus} />
      </div>
    </header>
  );
}
