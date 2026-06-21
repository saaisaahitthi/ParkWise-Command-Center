import { adaptEisScoreList } from "@/adapters/temporal";
import { apiGetLive } from "@/lib/api";
import type { BackendEISScoreListResponse } from "@/types/backend";
import type { EISScoreView } from "@/types/views";
import { fetchHotspotDisplayUniverse } from "@/services/hotspotDisplay";

export async function fetchEisScores(): Promise<EISScoreView[]> {
  const [raw, riskUniverse] = await Promise.all([
    apiGetLive<BackendEISScoreListResponse>("/eis/scores"),
    fetchHotspotDisplayUniverse(),
  ]);
  return adaptEisScoreList(raw, riskUniverse);
}
