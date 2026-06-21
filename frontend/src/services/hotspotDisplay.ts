import { apiGetLive } from "@/lib/api";
import type { BackendHotspotMapItem } from "@/types/backend";
import {
  applyPercentileRiskTiers,
  type DisplayMappedHotspot,
} from "@/utils/hotspotDisplay";

export type HotspotDisplayUniverseItem =
  DisplayMappedHotspot<BackendHotspotMapItem>;

export async function fetchHotspotDisplayUniverse(): Promise<
  HotspotDisplayUniverseItem[]
> {
  const hotspots =
    await apiGetLive<BackendHotspotMapItem[]>("/dashboard/map");
  return applyPercentileRiskTiers(hotspots);
}
