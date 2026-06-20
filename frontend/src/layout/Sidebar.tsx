import { NavLink, useLocation } from "react-router-dom";
import { Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import { NAV_ITEMS } from "@/constants/nav";
import { useAppStore } from "@/stores/appStore";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { ScrollArea } from "@/components/ui/scroll-area";

export function Sidebar() {
  const { sidebarCollapsed } = useAppStore();
  const location = useLocation();

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 flex h-screen flex-col transition-all duration-300 ease-in-out",
        "border-r border-[var(--color-sidebar-border)]",
        "bg-[var(--color-sidebar-bg)]"
      )}
      style={{ width: sidebarCollapsed ? "var(--sidebar-collapsed-width)" : "var(--sidebar-width)" }}
    >
      <NavLink
        to="/landing"
        className={cn(
          "flex h-[var(--topbar-height)] items-center justify-center border-b border-[var(--color-sidebar-border)]",
          "px-0"
        )}
      >
        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-900 text-[var(--color-primary)] shadow-[0_0_0_4px_rgba(0,212,255,0.08)] transition hover:bg-slate-800">
          <Shield className="h-5 w-5" />
        </div>
      </NavLink>

      {/* ── Navigation ── */}
      <ScrollArea className="flex-1 py-3">
        <nav className="flex flex-col gap-2 px-2">
          {NAV_ITEMS.map((item) => {
            const isActive =
              location.pathname === item.path ||
              (item.path !== "/dashboard" && location.pathname.startsWith(item.path));

            const linkContent = (
              <NavLink
                to={item.path}
                className={cn(
                  "group flex h-14 w-full items-center justify-center rounded-3xl transition-colors",
                  isActive
                    ? "bg-[rgba(0,212,255,0.14)] text-[var(--color-sidebar-text-active)] shadow-[0_0_0_8px_rgba(0,212,255,0.12)]"
                    : "text-[var(--color-sidebar-text)] hover:bg-[var(--color-sidebar-hover)] hover:text-[var(--color-sidebar-text-active)]"
                )}
              >
                <item.icon
                  className={cn(
                    "h-6 w-6 transition-colors",
                    isActive
                      ? "text-[var(--color-sidebar-icon-active)]"
                      : "text-[var(--color-sidebar-icon)] group-hover:text-[var(--color-sidebar-icon-active)]"
                  )}
                />
              </NavLink>
            );

            if (sidebarCollapsed) {
              return (
                <Tooltip key={item.key} delayDuration={0}>
                  <TooltipTrigger asChild>{linkContent}</TooltipTrigger>
                  <TooltipContent side="right" className="flex items-center gap-2">
                    {item.label}
                    {item.badge && <span className="text-purple-300">{item.badge}</span>}
                  </TooltipContent>
                </Tooltip>
              );
            }

            return <div key={item.key}>{linkContent}</div>;
          })}
        </nav>
      </ScrollArea>

      <div className="border-t border-[var(--color-sidebar-border)] p-2">
        <div className="flex items-center justify-center gap-2">
          <span className="h-3 w-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.35)]" />
          <span className="text-[11px] uppercase tracking-[0.25em] text-slate-400">API</span>
        </div>
        <div className="mt-2 flex items-center justify-center gap-2">
          <span className="h-3 w-3 rounded-full bg-amber-400" />
          <span className="text-[11px] uppercase tracking-[0.25em] text-slate-400">DB</span>
        </div>
      </div>
    </aside>
  );
}
