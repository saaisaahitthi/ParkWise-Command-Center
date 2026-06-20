/** Raw shapes returned by the FastAPI backend (source of truth). */

export interface BackendRiskDistribution {
  Critical: number;
  High: number;
  Medium: number;
  Low: number;
}

export interface BackendExecutiveSummary {
  total_hotspots: number;
  active_hotspots: number;
  critical_hotspots: number;
  high_risk_hotspots: number;
  total_forecasts: number;
  total_allocated_officers: number;
  latest_route_distance_km: number | null;
  latest_route_duration_min: number | null;
  last_updated_at: string | null;
}

export interface BackendHotspotMapItem {
  hotspot_id: number;
  name: string | null;
  latitude: number;
  longitude: number;
  hotspot_type: string | null;
  violation_count: number;
  latest_eis: number | null;
  risk_category: string | null;
  forecasted_eis: number | null;
  officers_allocated: number | null;
}

export interface BackendDashboardFull {
  executive_summary: BackendExecutiveSummary;
  risk_distribution: BackendRiskDistribution;
  hotspot_map: BackendHotspotMapItem[];
  temporal_overview: Record<string, unknown>;
  forecast_overview: Record<string, unknown>;
  allocation_overview: Record<string, unknown>;
  routing_overview: Record<string, unknown>;
}

export interface BackendForecastSummary {
  total_forecasts: number;
  average_predicted_eis: number;
  max_predicted_eis: number;
  risk_distribution: Record<string, number>;
  horizon_distribution: Record<string, number>;
  latest_generated_at: string | null;
  trained_horizons?: number[];
  models_in_memory?: number;
}

export interface BackendForecastItem {
  forecast_id: number;
  hotspot_id: number;
  forecast_date: string;
  horizon_days: number;
  predicted_eis: number;
  predicted_risk_category: string;
  confidence?: number;
  confidence_lower: number | null;
  confidence_upper: number | null;
  top_features?: unknown;
  model_version?: string | null;
  created_at?: string;
}

export interface BackendRouteStop {
  sequence: number;
  hotspot_id: number;
  hotspot_name?: string | null;
  latitude?: number;
  longitude?: number;
  lat?: number;
  lon?: number;
  risk_category?: string;
  eis_snapshot?: number | null;
  officers_allocated?: number;
  priority_rank?: number;
}

export interface BackendRouteLatest {
  route_id: number;
  route_name?: string | null;
  shift_label?: string | null;
  officer_count: number;
  total_distance_km?: number | null;
  estimated_duration_min?: number | null;
  hotspots_covered?: number | null;
  total_eis_covered?: number | null;
  stops?: BackendRouteStop[];
  created_at?: string | null;
}

export interface BackendGenerateRouteResponse {
  route_id: number;
  total_stops: number;
  critical_stops: number;
  high_stops: number;
  total_distance_km: number;
  estimated_travel_minutes: number;
  estimated_total_minutes: number;
  route_geometry: Array<{ lat: number; lng: number }>;
  stops: BackendRouteStop[];
}

export interface BackendEISComponentBreakdown {
  frequency_score: number;
  recurrence_score: number;
  density_score: number;
  temporal_risk_score: number;
  severity_norm: number;
  exposure_score: number;
  severity_multiplier: number;
}

export interface BackendEISScore {
  id: number;
  hotspot_id: number;
  eis_score: number;
  risk_category: string;
  rank: number | null;
  computed_for_date: string;
  components: BackendEISComponentBreakdown | null;
  created_at: string;
}

export interface BackendEISScoreListResponse {
  total: number;
  items: BackendEISScore[];
}

export interface BackendAllocationItem {
  id: number;
  hotspot_id: number;
  hotspot_name: string | null;
  officers_allocated: number;
  allocation_fraction: number;
  priority_rank: number;
  deployment_window: string | null;
  eis_snapshot: number | null;
  risk_category: string | null;
  allocation_date: string;
}

export interface BackendAllocationPlan {
  total_officers: number;
  hotspots_covered: number;
  allocations: BackendAllocationItem[];
  unallocated_officers: number;
  computed_at: string;
}
