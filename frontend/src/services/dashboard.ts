import { adaptDashboard } from "@/adapters/dashboard";
import { apiGetLive } from "@/lib/api";
import type {
  BackendAllocationPlan,
  BackendDashboardFull,
} from "@/types/backend";
import type { DashboardView } from "@/types/views";

export async function fetchDashboard(): Promise<DashboardView> {
  const [dashboard, latestAllocation] = await Promise.all([
    apiGetLive<BackendDashboardFull>("/dashboard/full"),
    apiGetLive<BackendAllocationPlan>("/allocation/latest"),
  ]);
  return adaptDashboard(dashboard, latestAllocation);
}
