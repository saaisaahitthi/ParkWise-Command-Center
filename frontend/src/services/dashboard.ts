import { adaptDashboard } from "@/adapters/dashboard";
import { apiGet } from "@/lib/api";
import type { BackendDashboardFull } from "@/types/backend";
import type { DashboardView } from "@/types/views";

export async function fetchDashboard(): Promise<DashboardView> {
  const raw = await apiGet<BackendDashboardFull>("/dashboard/full");
  return adaptDashboard(raw);
}
