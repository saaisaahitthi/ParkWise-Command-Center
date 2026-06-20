import type {
  BackendGenerateRouteResponse,
  BackendRouteLatest,
  BackendRouteStop,
} from "@/types/backend";
import type { PatrolRouteView, PatrolStopView } from "@/types/views";

function stopCoordinates(stop: BackendRouteStop): { lat: number; lng: number } {
  const lat = stop.latitude ?? stop.lat ?? 0;
  const lng = stop.longitude ?? stop.lon ?? 0;
  return { lat, lng };
}

function adaptStop(stop: BackendRouteStop): PatrolStopView {
  const { lat, lng } = stopCoordinates(stop);
  return {
    sequence: stop.sequence,
    name: stop.hotspot_name ?? `Hotspot #${stop.hotspot_id}`,
    risk: stop.risk_category ?? "Medium",
    lat,
    lng,
  };
}

function geometryFromStops(stops: PatrolStopView[]): Array<{ lat: number; lng: number }> {
  return stops.map(({ lat, lng }) => ({ lat, lng }));
}

export function adaptPatrolRouteFromLatest(
  route: BackendRouteLatest
): PatrolRouteView {
  const stop_sequence = (route.stops ?? []).map(adaptStop);
  const critical_high_stops = stop_sequence.filter(
    (s) => s.risk === "Critical" || s.risk === "High"
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
  response: BackendGenerateRouteResponse
): PatrolRouteView {
  const stop_sequence = (response.stops ?? []).map(adaptStop);
  return {
    route_id: response.route_id,
    total_stops: response.total_stops,
    critical_high_stops: response.critical_stops + response.high_stops,
    total_distance_km: response.total_distance_km,
    estimated_travel_time_minutes: response.estimated_total_minutes,
    route_geometry: response.route_geometry?.length
      ? response.route_geometry
      : geometryFromStops(stop_sequence),
    stop_sequence,
  };
}
