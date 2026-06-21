/** UI-facing view models (adapted from backend responses). */
import type { DisplayRiskTier } from "@/utils/hotspotDisplay";

export interface RiskChartSegment {
  name: string;
  value: number;
  color: string;
}

export interface DashboardMetric {
  label: string;
  value: number | string;
  delta: string;
}

export interface DashboardHotspotMarker {
  hotspot_id: number;
  name: string;
  latitude: number;
  longitude: number;
  hotspot_type: string;
  violation_count: number;
  latest_eis: number | null;
  risk_category: string;
  displayRiskTier: DisplayRiskTier;
  displayRiskScore: number;
  displayRiskRank: number;
  forecasted_eis: number | null;
  officers_allocated: number | null;
  displayName: string;
  displaySubtext: string | null;
}

export interface DashboardView {
  metrics: DashboardMetric[];
  riskChart: RiskChartSegment[];
  hotspotMap: DashboardHotspotMarker[];
  lastUpdatedAt: string | null;
}

export interface ForecastSummaryView {
  totalForecasts: number;
  forecastHorizonLabel: string;
  predictedHighRiskHotspots: number;
  avgPredictedEis: number;
}

export interface ForecastPredictionRow {
  hotspot_id: number;
  name: string;
  current_eis: number | null;
  forecasted_eis: number;
  risk_category: string;
  displayName: string;
  displaySubtext: string | null;
  displayRiskTier: DisplayRiskTier;
  action_recommended: string;
}

export interface PatrolStopView {
  sequence: number;
  hotspot_id: number;
  name: string;
  risk: string;
  displayName: string;
  displaySubtext: string | null;
  displayRiskTier: DisplayRiskTier;
  lat: number;
  lng: number;
}

export interface PatrolRouteView {
  route_id: number;
  total_stops: number;
  critical_high_stops: number;
  total_distance_km: number;
  estimated_travel_time_minutes: number;
  route_geometry: Array<{ lat: number; lng: number }>;
  stop_sequence: PatrolStopView[];
}

export interface EISScoreView {
  id: number;
  rank: number | null;
  hotspot_id: number;
  hotspot_label: string;
  eis_score: number;
  risk_category: string;
  displayName: string;
  displaySubtext: string | null;
  displayRiskTier: DisplayRiskTier;
  frequency_score: number;
  recurrence_score: number;
  density_score: number;
  temporal_risk_score: number;
  severity_norm: number;
  exposure_score: number;
  severity_multiplier: number;
}

export interface AllocationRowView {
  hotspot_id: number;
  hotspot_name: string;
  officers_allocated: number;
  risk_category: string;
  displayName: string;
  displaySubtext: string | null;
  displayRiskTier: DisplayRiskTier;
  priority: number;
}

export interface AllocationPlanView {
  total_officers_requested: number;
  total_officers_allocated: number;
  hotspots_covered: number;
  deployment_window: string;
  unallocated_officers: number;
  computed_at: string;
  allocations: AllocationRowView[];
}
