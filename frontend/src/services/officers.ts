import { adaptAllocationPlan } from "@/adapters/allocation";
import { fetchHotspotDisplayUniverse } from "@/services/hotspotDisplay";
import { apiGetLive, apiPostLive } from "@/lib/api";
import type {
  BackendAllocationPlan,
} from "@/types/backend";
import type { AllocationPlanView } from "@/types/views";

export async function fetchLatestAllocation(): Promise<AllocationPlanView> {
  const [raw, riskUniverse] = await Promise.all([
    apiGetLive<BackendAllocationPlan>("/allocation/latest"),
    fetchHotspotDisplayUniverse(),
  ]);
  return adaptAllocationPlan(raw, riskUniverse);
}

export async function computeAllocation(params: {
  total_officers: number;
  top_n_hotspots: number;
}): Promise<AllocationPlanView> {
  const raw = await apiPostLive<BackendAllocationPlan>("/allocation/compute", params);
  const riskUniverse = await fetchHotspotDisplayUniverse();
  return adaptAllocationPlan(raw, riskUniverse);
}
