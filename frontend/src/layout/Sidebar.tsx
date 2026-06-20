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
        "fixed left-0 top-0 z-40 flex h-screen flex-col border-r transition-all duration-300 ease-in-out",
        "border-white/[0.065] bg-[linear-gradient(180deg,#0c1721_0%,#081019_100%)]",
        "shadow-[20px_0_55px_-38px_rgba(34,211,238,0.4)]"
      )}
      style={{
        width: sidebarCollapsed
          ? "var(--sidebar-collapsed-width)"
          : "var(--sidebar-width)",
      }}
    >
      <NavLink
        to="/landing"
        className="flex h-[var(--topbar-height)] items-center justify-center border-b border-white/[0.06]"
        aria-label="ParkWise command overview"
      >
        <div className="flex h-10 w-10 items-center justify-center rounded-[14px] border border-cyan-300/18 bg-cyan-300/[0.075] text-[var(--color-primary)] shadow-[0_0_26px_-9px_rgba(79,209,197,0.75)] transition duration-300 hover:scale-105 hover:border-cyan-200/25 hover:bg-cyan-300/[0.12]">
          <Shield className="h-5 w-5" />
        </div>
      </NavLink>

      <ScrollArea className="flex-1 py-4">
        <nav className="flex flex-col gap-2.5 px-2.5">
          {NAV_ITEMS.map((item) => {
            const isActive =
              location.pathname === item.path ||
              (item.path !== "/dashboard" &&
                location.pathname.startsWith(item.path));

            return (
              <Tooltip key={item.key} delayDuration={80}>
                <TooltipTrigger asChild>
                  <NavLink
                    to={item.path}
                    className={cn(
                      "group relative flex h-12 w-full items-center justify-center overflow-hidden rounded-[15px] border transition-all duration-300",
                      isActive
                        ? "border-cyan-300/18 bg-[linear-gradient(145deg,rgba(103,232,249,0.14),rgba(34,211,238,0.055))] text-white shadow-[0_0_28px_-10px_rgba(79,209,197,0.9)]"
                        : "border-transparent text-[var(--color-sidebar-text)] hover:-translate-y-0.5 hover:border-white/[0.075] hover:bg-white/[0.05] hover:text-white"
                    )}
                    aria-label={item.label}
                  >
                    {isActive && (
                      <span className="absolute left-0 h-5 w-0.5 rounded-r-full bg-cyan-300 shadow-[0_0_10px_rgba(79,209,197,0.9)]" />
                    )}
                    <item.icon
                      className={cn(
                        "h-5 w-5 transition-all duration-300 group-hover:scale-105",
                        isActive
                          ? "text-[var(--color-sidebar-icon-active)]"
                          : "text-[var(--color-sidebar-icon)] group-hover:text-[var(--color-sidebar-icon-active)]"
                      )}
                    />
                  </NavLink>
                </TooltipTrigger>
                <TooltipContent
                  side="right"
                  sideOffset={10}
                  className="flex items-center gap-2 rounded-xl border border-white/10 bg-slate-950/95 px-3 py-2 text-xs font-medium shadow-xl shadow-black/30"
                >
                  {item.label}
                  {item.badge && (
                    <span className="text-violet-300">{item.badge}</span>
                  )}
                </TooltipContent>
              </Tooltip>
            );
          })}
        </nav>
      </ScrollArea>
    </aside>
  );
}
