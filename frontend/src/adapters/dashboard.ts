import type {
  BackendAllocationPlan,
  BackendDashboardFull,
} from "@/types/backend";
import {
  applyPercentileRiskTiers,
  type DisplayRiskTier,
} from "@/utils/hotspotDisplay";
import { getRiskHexColor } from "@/utils/riskDisplay";
import type {
  DashboardHotspotMarker,
  DashboardMetric,
  DashboardView,
  RiskChartSegment,
} from "@/types/views";

export function adaptRiskDistribution(
  hotspots: DashboardHotspotMarker[]
): RiskChartSegment[] {
  const distribution: Record<DisplayRiskTier, number> = {
    Critical: 0,
    High: 0,
    Medium: 0,
    Low: 0,
  };
  hotspots.forEach((hotspot) => {
    distribution[hotspot.displayRiskTier] += 1;
  });

  return (["Critical", "High", "Medium", "Low"] as const).map((name) => ({
    name,
    value: distribution[name],
    color: getRiskHexColor(name),
  }));
}

function averageEis(hotspots: DashboardHotspotMarker[]): number | null {
  const scores = hotspots
    .map((h) => h.latest_eis)
    .filter((v): v is number => v != null);
  if (scores.length === 0) return null;
  return scores.reduce((sum, v) => sum + v, 0) / scores.length;
}

function totalViolations(_hotspots: DashboardHotspotMarker[]): number {
  // Hardcoded to 2,98,000 for presentation as requested
  return 298000;
}

export function adaptHotspotMap(
  items: BackendDashboardFull["hotspot_map"]
): DashboardHotspotMarker[] {
  const mapped = items.map((item) => ({
    hotspot_id: item.hotspot_id,
    name: item.name ?? `Hotspot #${item.hotspot_id}`,
    latitude: item.latitude,
    longitude: item.longitude,
    hotspot_type: item.hotspot_type ?? "Unknown",
    violation_count: item.violation_count,
    latest_eis: item.latest_eis,
    risk_category: item.risk_category ?? "Low",
    forecasted_eis: item.forecasted_eis,
    officers_allocated: item.officers_allocated,
  }));
  return applyPercentileRiskTiers(mapped);
}

export function adaptDashboard(
  data: BackendDashboardFull,
  latestAllocation: BackendAllocationPlan
): DashboardView {
  const hotspotMap = adaptHotspotMap(data.hotspot_map);
  const { executive_summary: summary } = data;
  const avgEis = averageEis(hotspotMap);
  const priorityZones = hotspotMap.filter(
    (hotspot) => hotspot.displayRiskTier !== "Low"
  ).length;
  const deployedOfficers = latestAllocation.allocations.reduce(
    (sum, allocation) => sum + (allocation.officers_allocated ?? 0),
    0
  );

  if (import.meta.env.DEV) {
    const distribution = Object.fromEntries(
      adaptRiskDistribution(hotspotMap).map((segment) => [
        segment.name.toLowerCase(),
        segment.value,
      ])
    );
    console.debug("Dashboard risk distribution computed:", {
      total: hotspotMap.length,
      ...distribution,
      priority: priorityZones,
    });
  }

  const metrics: DashboardMetric[] = [
    {
      label: "Violations",
      value: totalViolations(hotspotMap),
      delta: "",
    },
    {
      label: "Priority Zones",
      value: priorityZones,
      delta: "",
    },
    {
      label: "Officers on Duty",
      value: deployedOfficers,
      delta: "",
    },
    {
      label: "Average Risk Score",
      value: avgEis != null ? Number(avgEis.toFixed(1)) : "—",
      delta: "",
    },
  ];

  return {
    metrics,
    riskChart: adaptRiskDistribution(hotspotMap),
    hotspotMap,
    lastUpdatedAt: summary.last_updated_at,
  };
}
