import { Outlet } from "react-router-dom";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { StatusBar } from "./StatusBar";
import { useAppStore } from "@/stores/appStore";
import { cn } from "@/lib/utils";

export function AppShell() {
  const { sidebarCollapsed } = useAppStore();

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-[var(--color-page-bg)]">
        {/* Sidebar */}
        <Sidebar />

        {/* Topbar */}
        <Topbar />

        {/* Main content */}
        <main
          className={cn(
            "flex flex-col transition-all duration-300",
            "min-h-screen"
          )}
          style={{
            paddingLeft: sidebarCollapsed
              ? "var(--sidebar-collapsed-width)"
              : "var(--sidebar-width)",
            paddingTop: "var(--topbar-height)",
            paddingBottom: "var(--statusbar-height)",
          }}
        >
          <div className="flex-1 p-6">
            <Outlet />
          </div>
        </main>

        {/* Status bar */}
        <StatusBar />
      </div>
    </TooltipProvider>
  );
}
