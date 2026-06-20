import { useQuery } from "@tanstack/react-query";
import { fetchHotspots, fetchZoneById, type HotspotsParams } from "@/services/hotspots";

export function useHotspots(params?: HotspotsParams) {
  return useQuery({
    queryKey: ["hotspots", params],
    queryFn: () => fetchHotspots(params),
  });
}

export function useZone(zoneId: string) {
  return useQuery({
    queryKey: ["zone", zoneId],
    queryFn: () => fetchZoneById(zoneId),
    enabled: !!zoneId,
  });
}
