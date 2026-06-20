import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  MapPin,
  Clock,
  TrendingUp,
  Users,
  Route,
  FlaskConical,
} from "lucide-react";

export interface NavItem {
  key: string;
  label: string;
  path: string;
  icon: LucideIcon;
  badge?: string;
}

export const NAV_ITEMS: NavItem[] = [
  { key: "dashboard", label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
  { key: "hotspots", label: "Hotspots", path: "/hotspots", icon: MapPin },
  { key: "temporal", label: "Temporal Analysis", path: "/temporal", icon: Clock },
  { key: "forecast", label: "Forecast", path: "/forecast", icon: TrendingUp },
  { key: "officers", label: "Officer Allocation", path: "/officers", icon: Users },
  { key: "patrol", label: "Patrol Routes", path: "/patrol", icon: Route },
  { key: "simulator", label: "Simulator", path: "/simulator", icon: FlaskConical, badge: "Beta" },
];
