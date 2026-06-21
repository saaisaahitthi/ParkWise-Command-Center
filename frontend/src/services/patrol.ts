import {
  adaptPatrolRouteFromDetail,
  adaptPatrolRouteFromGenerate,
} from "@/adapters/patrol";
import { fetchHotspotDisplayUniverse } from "@/services/hotspotDisplay";
import { apiGetLive, apiPostLive } from "@/lib/api";
import type {
  BackendGenerateRouteResponse,
  BackendPatrolRouteDetail,
  BackendRouteLatest,
} from "@/types/backend";
import type { PatrolRouteView } from "@/types/views";

export async function fetchLatestPatrolRoute(): Promise<PatrolRouteView> {
  const [summary, riskUniverse] = await Promise.all([
    apiGetLive<BackendRouteLatest>("/routing/latest"),
    fetchHotspotDisplayUniverse(),
  ]);
  const detail = await apiGetLive<BackendPatrolRouteDetail>(`/patrol/${summary.route_id}`);
  return adaptPatrolRouteFromDetail(detail, riskUniverse);
}

export async function generatePatrolRoute(): Promise<PatrolRouteView> {
  const raw = await apiPostLive<BackendGenerateRouteResponse>("/routing/generate", {
    route_date: new Date().toISOString().split("T")[0],
    shift_name: "default",
    max_stops: 10,
    use_two_opt: true,
  });
  const riskUniverse = await fetchHotspotDisplayUniverse();
  return adaptPatrolRouteFromGenerate(raw, riskUniverse);
}
