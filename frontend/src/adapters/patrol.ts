import type {
  BackendGenerateRouteResponse,
  BackendPatrolRouteDetail,
  BackendRouteLatest,
  BackendRouteStop,
} from "@/types/backend";
import type { PatrolRouteView, PatrolStopView } from "@/types/views";
import type { HotspotDisplayUniverseItem } from "@/services/hotspotDisplay";
import {
  getHotspotDisplayName,
  getHotspotSubtext,
  type DisplayRiskTier,
} from "@/utils/hotspotDisplay";

function stopCoordinates(stop: BackendRouteStop): { lat: number; lng: number } {
  const lat = stop.latitude ?? stop.lat ?? 0;
  const lng = stop.longitude ?? stop.lon ?? 0;
  return { lat, lng };
}

function adaptStop(
  stop: BackendRouteStop,
  tierByHotspot: Map<number, DisplayRiskTier>
): PatrolStopView {
  const { lat, lng } = stopCoordinates(stop);
  const displaySource = {
    hotspot_id: stop.hotspot_id,
    hotspot_name: stop.hotspot_name,
    lat,
    lng,
  };
  return {
    sequence: stop.sequence,
    hotspot_id: stop.hotspot_id,
    name: stop.hotspot_name ?? `Hotspot #${stop.hotspot_id}`,
    risk: stop.risk_category ?? "Medium",
    displayName: getHotspotDisplayName(displaySource),
    displaySubtext: getHotspotSubtext(displaySource),
    displayRiskTier: tierByHotspot.get(stop.hotspot_id) ?? "Low",
    lat,
    lng,
  };
}

function riskFromEis(score: number | null | undefined): string {
  if (score == null) return "Low";
  if (score >= 75) return "Critical";
  if (score >= 50) return "High";
  if (score >= 25) return "Medium";
  return "Low";
}

function geometryFromStops(stops: PatrolStopView[]): Array<{ lat: number; lng: number }> {
  return stops.map(({ lat, lng }) => ({ lat, lng }));
}

export function adaptPatrolRouteFromLatest(
  route: BackendRouteLatest,
  riskUniverse: HotspotDisplayUniverseItem[] = []
): PatrolRouteView {
  const tierByHotspot = new Map(
    riskUniverse.map((score) => [score.hotspot_id, score.displayRiskTier])
  );
  const stop_sequence = (route.stops ?? []).map((stop) =>
    adaptStop(stop, tierByHotspot)
  );
  const critical_high_stops = stop_sequence.filter(
    (s) =>
      s.displayRiskTier === "Critical" || s.displayRiskTier === "High"
  ).length;

  return {
    route_id: route.route_id,
    total_stops: route.hotspots_covered ?? stop_sequence.length,
    critical_high_stops,
    total_distance_km: route.total_distance_km ?? 0,
    estimated_travel_time_minutes: route.estimated_duration_min ?? 0,
    route_geometry: geometryFromStops(stop_sequence),
    stop_sequence,
  };
}

export function adaptPatrolRouteFromGenerate(
  response: BackendGenerateRouteResponse,
  riskUniverse: HotspotDisplayUniverseItem[] = []
): PatrolRouteView {
  const tierByHotspot = new Map(
    riskUniverse.map((score) => [score.hotspot_id, score.displayRiskTier])
  );
  const stop_sequence = (response.stops ?? []).map((stop) =>
    adaptStop(stop, tierByHotspot)
  );
  return {
    route_id: response.route_id,
    total_stops: response.total_stops,
    critical_high_stops: stop_sequence.filter(
      (stop) =>
        stop.displayRiskTier === "Critical" ||
        stop.displayRiskTier === "High"
    ).length,
    total_distance_km: response.total_distance_km,
    estimated_travel_time_minutes: response.estimated_total_minutes,
    route_geometry: response.route_geometry?.length
      ? response.route_geometry
      : geometryFromStops(stop_sequence),
    stop_sequence,
  };
}

export function adaptPatrolRouteFromDetail(
  route: BackendPatrolRouteDetail,
  riskUniverse: HotspotDisplayUniverseItem[] = []
): PatrolRouteView {
  const tierByHotspot = new Map(
    riskUniverse.map((score) => [score.hotspot_id, score.displayRiskTier])
  );
  const stop_sequence = route.stops.map((stop) =>
    adaptStop({
      sequence: stop.sequence,
      hotspot_id: stop.hotspot_id,
      hotspot_name: stop.hotspot_name,
      lat: stop.lat,
      lon: stop.lon,
      eis_snapshot: stop.eis_score,
      risk_category: riskFromEis(stop.eis_score),
    }, tierByHotspot)
  );

  return {
    route_id: route.id,
    total_stops: route.hotspots_covered ?? stop_sequence.length,
    critical_high_stops: stop_sequence.filter(
      (stop) =>
        stop.displayRiskTier === "Critical" ||
        stop.displayRiskTier === "High"
    ).length,
    total_distance_km: route.total_distance_km ?? 0,
    estimated_travel_time_minutes: route.estimated_duration_min ?? 0,
    route_geometry: geometryFromStops(stop_sequence),
    stop_sequence,
  };
}
