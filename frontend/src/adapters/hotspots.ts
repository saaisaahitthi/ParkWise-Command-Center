import type { HotspotRecord } from "@/services/hotspots";
import type { HotspotDisplayUniverseItem } from "@/services/hotspotDisplay";
import {
  getHotspotDisplayName,
  getHotspotSubtext,
  type DisplayRiskTier,
} from "@/utils/hotspotDisplay";

export type HotspotDisplayRecord = HotspotRecord & {
  displayName: string;
  displaySubtext: string | null;
  displayRiskTier: DisplayRiskTier;
  displayRiskScore: number;
  displayRiskRank: number;
};

export function adaptHotspotRecords(
  records: HotspotRecord[],
  riskUniverse: HotspotDisplayUniverseItem[]
): HotspotDisplayRecord[] {
  const riskByHotspot = new Map(
    riskUniverse.map((score) => [score.hotspot_id, score])
  );

  return records.map((record) => {
    const ranked = riskByHotspot.get(record.id);
    return {
      ...record,
      displayName: getHotspotDisplayName({
        ...record,
        hotspot_id: record.id,
      }),
      displaySubtext: getHotspotSubtext(record),
      displayRiskTier: ranked?.displayRiskTier ?? "Low",
      displayRiskScore: ranked?.displayRiskScore ?? record.total_violations,
      displayRiskRank: ranked?.displayRiskRank ?? riskUniverse.length + 1,
    };
  });
}
