import { Outlet, useLocation } from "react-router-dom";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { useAppStore } from "@/stores/appStore";
import { cn } from "@/lib/utils";

export function AppShell() {
  const { sidebarCollapsed } = useAppStore();
  const location = useLocation();
  const isLanding = location.pathname === "/landing";

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-[var(--color-page-bg)]">
        {!isLanding && <Sidebar />}
        {!isLanding && <Topbar />}

        <main
          className={cn(
            "flex flex-col transition-all duration-300",
            "min-h-screen"
          )}
          style={{
            paddingLeft: isLanding
              ? 0
              : sidebarCollapsed
                ? "var(--sidebar-collapsed-width)"
                : "var(--sidebar-width)",
            paddingTop: isLanding ? 0 : "var(--topbar-height)",
          }}
        >
          <div className={cn("flex-1", !isLanding && "p-6")}>
            <Outlet />
          </div>
        </main>
      </div>
    </TooltipProvider>
  );
}
