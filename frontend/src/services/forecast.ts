import {
  adaptForecastSummary,
  adaptForecastTop,
  buildEisLookup,
} from "@/adapters/forecast";
import { adaptEisScoreList } from "@/adapters/temporal";
import { apiGet, apiPost } from "@/lib/api";
import type {
  BackendEISScoreListResponse,
  BackendForecastItem,
  BackendForecastSummary,
} from "@/types/backend";
import type { ForecastPredictionRow, ForecastSummaryView } from "@/types/views";

export async function fetchForecastSummary(): Promise<ForecastSummaryView> {
  const raw = await apiGet<BackendForecastSummary>("/forecast/summary");
  return adaptForecastSummary(raw);
}

export async function fetchTopForecasts(): Promise<ForecastPredictionRow[]> {
  const [forecasts, eisResponse] = await Promise.all([
    apiGet<BackendForecastItem[]>("/forecast/top"),
    apiGet<BackendEISScoreListResponse>("/eis/scores"),
  ]);

  const eisScores = adaptEisScoreList(eisResponse);
  const { eisByHotspot, hotspotNames } = buildEisLookup(eisScores);
  return adaptForecastTop(forecasts, eisByHotspot, hotspotNames);
}

export async function generateForecasts(): Promise<unknown> {
  return apiPost("/forecast/generate", { horizon_days: 1, replace_existing: true });
}
