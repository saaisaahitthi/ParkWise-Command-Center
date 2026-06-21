import { useQuery } from "@tanstack/react-query";
import { fetchHotspots, fetchZoneById, type HotspotsParams } from "@/services/hotspots";
import { fetchHotspotDisplayUniverse } from "@/services/hotspotDisplay";

export function useHotspots(params?: HotspotsParams) {
  return useQuery({
    queryKey: ["hotspots", params],
    queryFn: () => fetchHotspots(params),
    refetchInterval: 10_000,
  });
}

export function useZone(zoneId: string) {
  return useQuery({
    queryKey: ["zone", zoneId],
    queryFn: () => fetchZoneById(zoneId),
    enabled: !!zoneId,
  });
}

export function useHotspotDisplayUniverse() {
  return useQuery({
    queryKey: ["hotspot-display-universe"],
    queryFn: fetchHotspotDisplayUniverse,
    refetchInterval: 10_000,
  });
}
