import { useLocation } from "react-router-dom";
import { Bell, RefreshCw, ChevronDown, CircleDot } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAppStore } from "@/stores/appStore";
import { Button } from "@/components/ui/button";
import { NAV_ITEMS } from "@/constants/nav";

function usePageTitle(): string {
  const location = useLocation();
  const found = NAV_ITEMS.find(
    (item) =>
      location.pathname === item.path ||
      (item.path !== "/dashboard" && location.pathname.startsWith(item.path))
  );
  return found?.label ?? "Command Overview";
}

export function Topbar() {
  const { sidebarCollapsed, useMockData, toggleMockData } = useAppStore();
  const pageTitle = usePageTitle();

  return (
    <header
      className={cn(
        "fixed right-0 top-0 z-30 flex items-center justify-between gap-4 px-6",
        "border-b border-[var(--color-topbar-border)] bg-[var(--color-topbar-bg)] backdrop-blur-xl",
        "transition-all duration-300"
      )}
      style={{
        height: "var(--topbar-height)",
        left: sidebarCollapsed ? "var(--sidebar-collapsed-width)" : "var(--sidebar-width)",
      }}
    >
      <div className="flex min-w-0 items-center gap-5">
        <div className="rounded-3xl border border-slate-700 bg-slate-950/90 px-4 py-3 shadow-[0_20px_50px_-40px_rgba(0,0,0,0.6)]">
          <p className="text-[10px] uppercase tracking-[0.32em] text-slate-500">Jabalpur Command Center</p>
          <h1 className="mt-1 text-lg font-display font-semibold text-white leading-tight">
            {pageTitle}
          </h1>
        </div>
        <button
          onClick={toggleMockData}
          title="Click to toggle between Mock Data and Live API Mode"
          className={cn(
            "hidden xl:flex items-center gap-3 rounded-3xl border px-4 py-2.5 shadow-[0_20px_50px_-40px_rgba(0,0,0,0.6)] transition-all active:scale-95 cursor-pointer",
            useMockData
              ? "border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/15 text-amber-300"
              : "border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/15 text-emerald-300"
          )}
        >
          <span className={cn(
            "h-2 w-2 rounded-full",
            useMockData ? "bg-amber-400 animate-pulse" : "bg-emerald-400 animate-pulse"
          )} />
          <span className="text-xs uppercase font-bold tracking-[0.2em] font-display">
            {useMockData ? "Mock Simulation Mode" : "Live API Connected"}
          </span>
        </button>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden md:flex items-center gap-2 rounded-2xl bg-slate-900/80 px-3 py-2 text-sm text-slate-300">
          <CircleDot className="h-3.5 w-3.5 text-[var(--color-primary)]" />
          <span>City online</span>
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="relative h-10 w-10 rounded-2xl text-slate-300 hover:bg-slate-800 hover:text-white"
          aria-label="View notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-semibold text-white">
            3
          </span>
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 rounded-2xl text-slate-300 hover:bg-slate-800 hover:text-white"
          aria-label="Refresh dashboard"
        >
          <RefreshCw className="h-5 w-5" />
        </Button>

        <button
          className="hidden sm:flex items-center gap-2 rounded-2xl border border-slate-700 bg-slate-950/90 px-3 py-2 text-left transition hover:border-slate-500"
          aria-label="User profile menu"
        >
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-800 text-sm font-semibold text-slate-200">
            OP
          </div>
          <div className="hidden lg:flex flex-col leading-tight">
            <span className="text-sm font-semibold text-white">Operator</span>
            <span className="text-xs text-slate-500">Shift 2</span>
          </div>
          <ChevronDown className="h-4 w-4 text-slate-400" />
        </button>
      </div>
    </header>
  );
}
