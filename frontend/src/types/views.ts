/** UI-facing view models (adapted from backend responses). */

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
  forecasted_eis: number | null;
  officers_allocated: number | null;
}

export interface DashboardView {
  metrics: DashboardMetric[];
  riskChart: RiskChartSegment[];
  hotspotMap: DashboardHotspotMarker[];
  lastUpdatedAt: string | null;
}

export interface ForecastSummaryView {
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
  action_recommended: string;
}

export interface PatrolStopView {
  sequence: number;
  name: string;
  risk: string;
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
  priority: number;
}

export interface AllocationPlanView {
  total_officers_allocated: number;
  hotspots_covered: number;
  deployment_window: string;
  unallocated_officers: number;
  computed_at: string;
  allocations: AllocationRowView[];
}

export interface SimulatorPresetView {
  id: string;
  name: string;
  description: string;
  officers: number;
  top_n_hotspots: number | null;
}

export interface SimulatorBaselineView {
  baseline_coverage: number;
  baseline_eis_avg: number;
  total_hotspots: number;
  baseline_total_officers: number;
}

export interface SimulatorResultView {
  simulated_coverage: number;
  simulated_eis_avg: number;
  recommendation: string;
  improved_hotspots: number;
  worsened_hotspots: number;
}
