import apiClient from "@/lib/axios";
import type { ApiResponse, PaginatedResponse, Zone } from "@/types";

export interface HotspotsParams {
  page?: number;
  page_size?: number;
  zone_ids?: string[];
  from_date?: string;
  to_date?: string;
}

export async function fetchHotspots(params?: HotspotsParams): Promise<PaginatedResponse<Zone>> {
  const { data } = await apiClient.get<ApiResponse<PaginatedResponse<Zone>>>("/hotspots", {
    params,
  });
  return data.data;
}

export async function fetchZoneById(zoneId: string): Promise<Zone> {
  const { data } = await apiClient.get<ApiResponse<Zone>>(`/hotspots/${zoneId}`);
  return data.data;
}
