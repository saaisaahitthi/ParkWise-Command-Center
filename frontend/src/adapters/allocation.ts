import type { BackendAllocationPlan } from "@/types/backend";
import type { AllocationPlanView, AllocationRowView } from "@/types/views";

export function adaptAllocationPlan(plan: BackendAllocationPlan): AllocationPlanView {
  const allocations: AllocationRowView[] = plan.allocations.map((item) => ({
    hotspot_id: item.hotspot_id,
    hotspot_name: item.hotspot_name ?? `Hotspot #${item.hotspot_id}`,
    officers_allocated: item.officers_allocated,
    risk_category: item.risk_category ?? "Medium",
    priority: item.priority_rank,
  }));

  const deployed = allocations.reduce((sum, a) => sum + a.officers_allocated, 0);
  const firstWindow = plan.allocations.find((a) => a.deployment_window)?.deployment_window;

  return {
    total_officers_allocated: deployed || plan.total_officers,
    hotspots_covered: plan.hotspots_covered,
    deployment_window: firstWindow ?? formatComputedAt(plan.computed_at),
    unallocated_officers: plan.unallocated_officers,
    computed_at: plan.computed_at,
    allocations,
  };
}

function formatComputedAt(iso: string): string {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}
