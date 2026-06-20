import { useLocation } from "react-router-dom";
import { Bell, ChevronDown } from "lucide-react";
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
  const { sidebarCollapsed } = useAppStore();
  const pageTitle = usePageTitle();

  return (
    <header
      className={cn(
        "fixed right-0 top-0 z-30 flex items-center justify-between gap-4 px-6",
        "border-b border-white/[0.07] bg-[#08111a]/92 shadow-[0_18px_50px_-42px_rgba(34,211,238,0.35)] backdrop-blur-2xl",
        "transition-all duration-300"
      )}
      style={{
        height: "var(--topbar-height)",
        left: sidebarCollapsed ? "var(--sidebar-collapsed-width)" : "var(--sidebar-width)",
      }}
    >
      <div className="flex min-w-0 items-center">
        <div className="min-w-0">
          <p className="truncate text-[9px] font-semibold uppercase tracking-[0.3em] text-cyan-300/65">
            Bengaluru Command Center
          </p>
          <h1 className="mt-1 truncate font-display text-[19px] font-semibold leading-tight tracking-[0.01em] text-white">
            {pageTitle}
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          className="relative h-10 w-10 rounded-[14px] border border-transparent text-slate-400 transition hover:border-white/[0.08] hover:bg-white/[0.05] hover:text-white"
          aria-label="View notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[9px] font-semibold text-white">
            3
          </span>
        </Button>

        <button
          className="hidden items-center gap-2 rounded-2xl border border-white/[0.08] bg-white/[0.035] px-2.5 py-1.5 text-left shadow-lg shadow-black/10 transition hover:border-cyan-300/20 hover:bg-white/[0.055] sm:flex"
          aria-label="User profile menu"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-300/10 bg-cyan-300/[0.07] text-xs font-semibold text-cyan-100">
            OP
          </div>
          <div className="hidden lg:flex flex-col leading-tight">
            <span className="text-sm font-semibold text-white">Operator</span>
            <span className="text-[11px] text-slate-500">Control room</span>
          </div>
          <ChevronDown className="h-4 w-4 text-slate-400" />
        </button>
      </div>
    </header>
  );
}
