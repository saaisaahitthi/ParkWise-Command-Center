import type {
  BackendDashboardFull,
  BackendRiskDistribution,
} from "@/types/backend";
import type {
  DashboardHotspotMarker,
  DashboardMetric,
  DashboardView,
  RiskChartSegment,
} from "@/types/views";

const RISK_COLORS: Record<string, string> = {
  Critical: "#EF4444",
  High: "#F59E0B",
  Medium: "#3B82F6",
  Low: "#10B981",
};

export function adaptRiskDistribution(
  distribution: BackendRiskDistribution
): RiskChartSegment[] {
  return (["Critical", "High", "Medium", "Low"] as const).map((name) => ({
    name,
    value: distribution[name] ?? 0,
    color: RISK_COLORS[name],
  }));
}

function averageEis(hotspots: DashboardHotspotMarker[]): number | null {
  const scores = hotspots
    .map((h) => h.latest_eis)
    .filter((v): v is number => v != null);
  if (scores.length === 0) return null;
  return scores.reduce((sum, v) => sum + v, 0) / scores.length;
}

function totalViolations(hotspots: DashboardHotspotMarker[]): number {
  return hotspots.reduce((sum, h) => sum + (h.violation_count ?? 0), 0);
}

export function adaptHotspotMap(
  items: BackendDashboardFull["hotspot_map"]
): DashboardHotspotMarker[] {
  return items.map((item) => ({
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
}

export function adaptDashboard(data: BackendDashboardFull): DashboardView {
  const hotspotMap = adaptHotspotMap(data.hotspot_map);
  const { executive_summary: summary } = data;
  const avgEis = averageEis(hotspotMap);
  const highRiskZones = summary.critical_hotspots + summary.high_risk_hotspots;

  const metrics: DashboardMetric[] = [
    {
      label: "Violations",
      value: totalViolations(hotspotMap),
      delta: "",
    },
    {
      label: "High Risk Zones",
      value: highRiskZones,
      delta: "",
    },
    {
      label: "Officers on Duty",
      value: summary.total_allocated_officers,
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
    riskChart: adaptRiskDistribution(data.risk_distribution),
    hotspotMap,
    lastUpdatedAt: summary.last_updated_at,
  };
}
