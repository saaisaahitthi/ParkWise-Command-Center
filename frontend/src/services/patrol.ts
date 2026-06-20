import {
  adaptPatrolRouteFromGenerate,
  adaptPatrolRouteFromLatest,
} from "@/adapters/patrol";
import { apiGet, apiPost } from "@/lib/api";
import type {
  BackendGenerateRouteResponse,
  BackendRouteLatest,
} from "@/types/backend";
import type { PatrolRouteView } from "@/types/views";

export async function fetchLatestPatrolRoute(): Promise<PatrolRouteView> {
  const raw = await apiGet<BackendRouteLatest>("/routing/latest");
  return adaptPatrolRouteFromLatest(raw);
}

export async function generatePatrolRoute(): Promise<PatrolRouteView> {
  const raw = await apiPost<BackendGenerateRouteResponse>("/routing/generate", {
    route_date: new Date().toISOString().split("T")[0],
    shift_name: "default",
    max_stops: 10,
    use_two_opt: true,
  });
  return adaptPatrolRouteFromGenerate(raw);
}
