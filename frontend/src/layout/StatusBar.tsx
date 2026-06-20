import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/appStore";

export function StatusBar() {
  const { sidebarCollapsed } = useAppStore();
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  return (
    <footer
      className={cn(
        "fixed bottom-0 right-0 z-30 flex items-center gap-6 px-4",
        "border-t border-slate-200 bg-white text-[11px] text-slate-500",
        "transition-all duration-300"
      )}
      style={{
        height: "var(--statusbar-height)",
        left: sidebarCollapsed ? "var(--sidebar-collapsed-width)" : "var(--sidebar-width)",
      }}
    >
      {/* API status */}
      <div className="flex items-center gap-1.5">
        <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
        <span>API Connected</span>
      </div>

      <div className="h-3 w-px bg-slate-200" />

      {/* Last sync */}
      <span>
        Last sync:{" "}
        <span className="font-mono tabular-nums font-medium text-slate-600">
          {time.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
        </span>
      </span>

      <div className="h-3 w-px bg-slate-200" />

      {/* Data source */}
      <span>Source: Bengaluru Police — BBMP Violation Dataset</span>

      {/* Spacer */}
      <div className="flex-1" />

      <span>
        {import.meta.env.VITE_APP_NAME} v{import.meta.env.VITE_APP_VERSION}
      </span>
    </footer>
  );
}
