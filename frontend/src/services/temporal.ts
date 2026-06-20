import { adaptEisScoreList } from "@/adapters/temporal";
import { apiGet } from "@/lib/api";
import type { BackendEISScoreListResponse } from "@/types/backend";
import type { EISScoreView } from "@/types/views";

export async function fetchEisScores(): Promise<EISScoreView[]> {
  const raw = await apiGet<BackendEISScoreListResponse>("/eis/scores");
  return adaptEisScoreList(raw);
}
