import type { BackendForecastItem, BackendForecastSummary } from "@/types/backend";
import type { ForecastPredictionRow, ForecastSummaryView } from "@/types/views";
import type { EISScoreView } from "@/types/views";
import {
  getHotspotDisplayName,
  type DisplayRiskTier,
} from "@/utils/hotspotDisplay";

export function adaptForecastSummary(
  summary: BackendForecastSummary
): ForecastSummaryView {
  const horizons = Object.keys(summary.horizon_distribution ?? {});
  const primaryHorizon =
    horizons.length > 0
      ? Math.max(...horizons.map((h) => Number(h)))
      : summary.trained_horizons?.[0];

  const highRisk =
    (summary.risk_distribution?.Critical ?? 0) +
    (summary.risk_distribution?.High ?? 0);

  return {
    totalForecasts: summary.total_forecasts ?? 0,
    forecastHorizonLabel: primaryHorizon
      ? `${primaryHorizon} Day${Number(primaryHorizon) === 1 ? "" : "s"}`
      : "—",
    predictedHighRiskHotspots: highRisk,
    avgPredictedEis: summary.average_predicted_eis ?? 0,
  };
}

function deriveAction(item: BackendForecastItem): string {
  const features = item.top_features;
  if (features && typeof features === "object" && !Array.isArray(features)) {
    const topKey = Object.keys(features as Record<string, unknown>)[0];
    if (topKey) {
      return `Monitor ${topKey.replace(/_/g, " ")} — predicted ${item.predicted_risk_category} risk`;
    }
  }
  if (item.predicted_risk_category === "Critical") {
    return "Deploy surge patrol during next forecast horizon";
  }
  if (item.predicted_risk_category === "High") {
    return "Increase enforcement presence at peak windows";
  }
  return "Maintain standard patrol cadence";
}

export function adaptForecastTop(
  forecasts: BackendForecastItem[],
  eisByHotspot: Map<number, number>,
  hotspotNames: Map<number, string>,
  tierByHotspot: Map<number, DisplayRiskTier>
): ForecastPredictionRow[] {
  return forecasts.map((item) => {
    const name = hotspotNames.get(item.hotspot_id);
    return {
      hotspot_id: item.hotspot_id,
      name: name ?? `Hotspot #${item.hotspot_id}`,
      displayName: getHotspotDisplayName({
        hotspot_id: item.hotspot_id,
        hotspot_name: name,
      }),
      displaySubtext: null,
      displayRiskTier: tierByHotspot.get(item.hotspot_id) ?? "Low",
      current_eis: eisByHotspot.get(item.hotspot_id) ?? null,
      forecasted_eis: item.predicted_eis,
      risk_category: item.predicted_risk_category,
      action_recommended: deriveAction(item),
    };
  });
}

export function buildEisLookup(
  scores: EISScoreView[]
): {
  eisByHotspot: Map<number, number>;
  hotspotNames: Map<number, string>;
  tierByHotspot: Map<number, DisplayRiskTier>;
} {
  const eisByHotspot = new Map<number, number>();
  const hotspotNames = new Map<number, string>();
  const tierByHotspot = new Map<number, DisplayRiskTier>();
  for (const score of scores) {
    eisByHotspot.set(score.hotspot_id, score.eis_score);
    hotspotNames.set(score.hotspot_id, score.displayName);
    tierByHotspot.set(score.hotspot_id, score.displayRiskTier);
  }
  return { eisByHotspot, hotspotNames, tierByHotspot };
}
