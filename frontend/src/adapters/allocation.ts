import type { BackendAllocationPlan } from "@/types/backend";
import type { AllocationPlanView, AllocationRowView } from "@/types/views";
import type { HotspotDisplayUniverseItem } from "@/services/hotspotDisplay";
import {
  getHotspotDisplayName,
  getHotspotSubtext,
} from "@/utils/hotspotDisplay";

export function adaptAllocationPlan(
  plan: BackendAllocationPlan,
  riskUniverse: HotspotDisplayUniverseItem[]
): AllocationPlanView {
  const tierByHotspot = new Map(
    riskUniverse.map((score) => [score.hotspot_id, score.displayRiskTier])
  );
  const allocations: AllocationRowView[] = plan.allocations.map((item) => ({
    hotspot_id: item.hotspot_id,
    hotspot_name: item.hotspot_name ?? `Hotspot #${item.hotspot_id}`,
    officers_allocated: item.officers_allocated,
    risk_category: item.risk_category ?? "Medium",
    displayName: getHotspotDisplayName(item),
    displaySubtext: getHotspotSubtext(item),
    displayRiskTier: tierByHotspot.get(item.hotspot_id) ?? "Low",
    priority: item.priority_rank,
  }));

  const deployed = allocations.reduce((sum, a) => sum + a.officers_allocated, 0);
  const firstWindow = plan.allocations.find((a) => a.deployment_window)?.deployment_window;

  return {
    total_officers_requested: plan.total_officers,
    total_officers_allocated: deployed,
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
