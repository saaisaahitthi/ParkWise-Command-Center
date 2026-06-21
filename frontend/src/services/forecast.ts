import {
  adaptForecastSummary,
  adaptForecastTop,
  buildEisLookup,
} from "@/adapters/forecast";
import { adaptEisScoreList } from "@/adapters/temporal";
import { apiGetLive, apiPostLive } from "@/lib/api";
import type {
  BackendEISScoreListResponse,
  BackendForecastGenerateResponse,
  BackendForecastItem,
  BackendForecastSummary,
  BackendForecastTrainResponse,
} from "@/types/backend";
import type { ForecastPredictionRow, ForecastSummaryView } from "@/types/views";
import { fetchHotspotDisplayUniverse } from "@/services/hotspotDisplay";

export async function getForecastSummary(): Promise<ForecastSummaryView> {
  const raw = await apiGetLive<BackendForecastSummary>("/forecast/summary");
  return adaptForecastSummary(raw);
}

export async function getTopForecasts(): Promise<ForecastPredictionRow[]> {
  const [forecasts, eisResponse, riskUniverse] = await Promise.all([
    apiGetLive<BackendForecastItem[]>("/forecast/top"),
    apiGetLive<BackendEISScoreListResponse>("/eis/scores"),
    fetchHotspotDisplayUniverse(),
  ]);

  const eisScores = adaptEisScoreList(eisResponse, riskUniverse);
  const { eisByHotspot, hotspotNames, tierByHotspot } =
    buildEisLookup(eisScores);
  return adaptForecastTop(
    forecasts,
    eisByHotspot,
    hotspotNames,
    tierByHotspot
  );
}

export async function trainForecast(): Promise<BackendForecastTrainResponse> {
  return apiPostLive<BackendForecastTrainResponse>("/forecast/train", {
    horizon_days: 1,
    model_version: "forecast-v1-h1",
    min_history_per_hotspot: 1,
  });
}

export async function generateForecast(): Promise<BackendForecastGenerateResponse> {
  return apiPostLive<BackendForecastGenerateResponse>("/forecast/generate", {
    horizon_days: 1,
    hotspot_id: null,
    replace_existing: true,
    pipeline_run_id: "forecast-v1-h1",
  });
}

export const fetchForecastSummary = getForecastSummary;
export const fetchTopForecasts = getTopForecasts;
