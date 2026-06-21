import type { BackendEISScore, BackendEISScoreListResponse } from "@/types/backend";
import type { EISScoreView } from "@/types/views";
import type { HotspotDisplayUniverseItem } from "@/services/hotspotDisplay";
import {
  applyPercentileRiskTiers,
  getHotspotDisplayName,
} from "@/utils/hotspotDisplay";

/** Normalize component scores that may be stored as 0–1 or 0–100. */
export function normalizeComponentScore(value: number): number {
  if (value > 1) return value / 100;
  return value;
}

export function adaptEisScore(score: BackendEISScore): EISScoreView {
  const components = score.components;
  const frequency = normalizeComponentScore(components?.frequency_score ?? 0);
  const recurrence = normalizeComponentScore(components?.recurrence_score ?? 0);
  const density = normalizeComponentScore(components?.density_score ?? 0);
  const temporal = normalizeComponentScore(components?.temporal_risk_score ?? 0);
  const exposure = normalizeComponentScore(components?.exposure_score ?? 0);

  return {
    id: score.id,
    rank: score.rank,
    hotspot_id: score.hotspot_id,
    hotspot_label: `Hotspot #${score.hotspot_id}`,
    eis_score: score.eis_score,
    risk_category: score.risk_category,
    displayName: getHotspotDisplayName({ hotspot_id: score.hotspot_id }),
    displaySubtext: null,
    displayRiskTier: "Low",
    frequency_score: frequency,
    recurrence_score: recurrence,
    density_score: density,
    temporal_risk_score: temporal,
    severity_norm: components?.severity_norm ?? 0,
    exposure_score: exposure,
    severity_multiplier: components?.severity_multiplier ?? 1,
  };
}

export function adaptEisScoreList(
  response: BackendEISScoreListResponse,
  riskUniverse: HotspotDisplayUniverseItem[] = []
): EISScoreView[] {
  const scores = response.items.map(adaptEisScore);
  const ranked = riskUniverse.length
    ? riskUniverse
    : applyPercentileRiskTiers(
        scores.map((score) => ({
          hotspot_id: score.hotspot_id,
          eis_score: score.eis_score,
        }))
      );
  const tierByHotspot = new Map(
    ranked.map((score) => [score.hotspot_id, score.displayRiskTier])
  );
  const displayByHotspot = new Map(
    riskUniverse.map((hotspot) => [hotspot.hotspot_id, hotspot])
  );
  return scores.map((score) => ({
    ...score,
    displayName:
      displayByHotspot.get(score.hotspot_id)?.displayName ??
      score.displayName,
    displaySubtext:
      displayByHotspot.get(score.hotspot_id)?.displaySubtext ?? null,
    displayRiskTier: tierByHotspot.get(score.hotspot_id) ?? "Low",
  }));
}
