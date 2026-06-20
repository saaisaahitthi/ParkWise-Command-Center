import { adaptAllocationPlan } from "@/adapters/allocation";
import { apiGet, apiPost } from "@/lib/api";
import type { BackendAllocationPlan } from "@/types/backend";
import type { AllocationPlanView } from "@/types/views";

export async function fetchLatestAllocation(): Promise<AllocationPlanView> {
  const raw = await apiGet<BackendAllocationPlan>("/allocation/latest");
  return adaptAllocationPlan(raw);
}

export async function computeAllocation(params: {
  total_officers: number;
  top_n_hotspots: number;
}): Promise<AllocationPlanView> {
  const raw = await apiPost<BackendAllocationPlan>("/allocation/compute", params);
  return adaptAllocationPlan(raw);
}
