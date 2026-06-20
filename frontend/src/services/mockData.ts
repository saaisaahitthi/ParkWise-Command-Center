// Mock data shaped like backend API responses (Jabalpur Command Center)

export const mockDashboardFull = {
  executive_summary: {
    total_hotspots: 4,
    active_hotspots: 4,
    critical_hotspots: 1,
    high_risk_hotspots: 2,
    total_forecasts: 4,
    total_allocated_officers: 20,
    latest_route_distance_km: 8.4,
    latest_route_duration_min: 45,
    last_updated_at: new Date().toISOString(),
  },
  risk_distribution: {
    Critical: 1,
    High: 2,
    Medium: 1,
    Low: 0,
  },
  hotspot_map: [
    {
      hotspot_id: 1,
      name: "Civic Center Junction",
      latitude: 23.1678,
      longitude: 79.9322,
      hotspot_type: "Commercial Hub",
      violation_count: 482,
      latest_eis: 78.4,
      risk_category: "High",
      forecasted_eis: 85.2,
      officers_allocated: 6,
    },
    {
      hotspot_id: 2,
      name: "Jabalpur Railway Station",
      latitude: 23.1667,
      longitude: 79.95,
      hotspot_type: "Transit Node",
      violation_count: 703,
      latest_eis: 92.1,
      risk_category: "Critical",
      forecasted_eis: 94.5,
      officers_allocated: 8,
    },
    {
      hotspot_id: 3,
      name: "Gorakhpur Market Area",
      latitude: 23.1539,
      longitude: 79.9247,
      hotspot_type: "Shopping District",
      violation_count: 558,
      latest_eis: 81.5,
      risk_category: "High",
      forecasted_eis: 88.0,
      officers_allocated: 4,
    },
    {
      hotspot_id: 4,
      name: "Sadar Cantt Road",
      latitude: 23.1492,
      longitude: 79.9489,
      hotspot_type: "Main Thoroughfare",
      violation_count: 329,
      latest_eis: 58.2,
      risk_category: "Medium",
      forecasted_eis: 68.0,
      officers_allocated: 2,
    },
  ],
  temporal_overview: {},
  forecast_overview: {},
  allocation_overview: {},
  routing_overview: {},
};

export const mockHotspots = {
  items: [
    {
      id: 2,
      hotspot_name: "Jabalpur Railway Station",
      total_violations: 703,
      dominant_violation_type: "No Parking Zone",
      dominant_vehicle_category: "Auto-Rickshaw",
      unique_dates: 30,
      centroid_lat: 23.1667,
      centroid_lon: 79.95,
    },
    {
      id: 3,
      hotspot_name: "Gorakhpur Market Area",
      total_violations: 558,
      dominant_violation_type: "Obstruction",
      dominant_vehicle_category: "Four-Wheeler",
      unique_dates: 25,
      centroid_lat: 23.1539,
      centroid_lon: 79.9247,
    },
    {
      id: 1,
      hotspot_name: "Civic Center Junction",
      total_violations: 482,
      dominant_violation_type: "Double Parking",
      dominant_vehicle_category: "Two-Wheeler",
      unique_dates: 28,
      centroid_lat: 23.1678,
      centroid_lon: 79.9322,
    },
    {
      id: 4,
      hotspot_name: "Sadar Cantt Road",
      total_violations: 329,
      dominant_violation_type: "Double Parking",
      dominant_vehicle_category: "Four-Wheeler",
      unique_dates: 20,
      centroid_lat: 23.1492,
      centroid_lon: 79.9489,
    },
  ],
  total: 4,
  page: 1,
  page_size: 50,
  pages: 1,
};

export const mockEisScores = {
  total: 4,
  items: [
    {
      id: 1,
      rank: 1,
      hotspot_id: 2,
      eis_score: 92.1,
      risk_category: "Critical",
      computed_for_date: new Date().toISOString(),
      created_at: new Date().toISOString(),
      components: {
        frequency_score: 0.95,
        recurrence_score: 0.92,
        density_score: 0.88,
        temporal_risk_score: 0.91,
        severity_norm: 0.85,
        exposure_score: 0.9,
        severity_multiplier: 1.2,
      },
    },
    {
      id: 2,
      rank: 2,
      hotspot_id: 3,
      eis_score: 81.5,
      risk_category: "High",
      computed_for_date: new Date().toISOString(),
      created_at: new Date().toISOString(),
      components: {
        frequency_score: 0.84,
        recurrence_score: 0.81,
        density_score: 0.78,
        temporal_risk_score: 0.82,
        severity_norm: 0.75,
        exposure_score: 0.8,
        severity_multiplier: 1.15,
      },
    },
    {
      id: 3,
      rank: 3,
      hotspot_id: 1,
      eis_score: 78.4,
      risk_category: "High",
      computed_for_date: new Date().toISOString(),
      created_at: new Date().toISOString(),
      components: {
        frequency_score: 0.82,
        recurrence_score: 0.79,
        density_score: 0.75,
        temporal_risk_score: 0.8,
        severity_norm: 0.72,
        exposure_score: 0.78,
        severity_multiplier: 1.1,
      },
    },
    {
      id: 4,
      rank: 4,
      hotspot_id: 4,
      eis_score: 58.2,
      risk_category: "Medium",
      computed_for_date: new Date().toISOString(),
      created_at: new Date().toISOString(),
      components: {
        frequency_score: 0.6,
        recurrence_score: 0.58,
        density_score: 0.55,
        temporal_risk_score: 0.62,
        severity_norm: 0.5,
        exposure_score: 0.56,
        severity_multiplier: 1.0,
      },
    },
  ],
};

export const mockForecastSummary = {
  total_forecasts: 4,
  average_predicted_eis: 75.3,
  max_predicted_eis: 94.5,
  risk_distribution: { Critical: 1, High: 2, Medium: 1 },
  horizon_distribution: { "7": 4 },
  latest_generated_at: new Date().toISOString(),
  trained_horizons: [1, 7],
  models_in_memory: 2,
};

export const mockForecastTop = [
  {
    forecast_id: 1,
    hotspot_id: 2,
    forecast_date: new Date().toISOString(),
    horizon_days: 7,
    predicted_eis: 94.5,
    predicted_risk_category: "Critical",
    confidence_lower: 88.0,
    confidence_upper: 98.0,
    top_features: { temporal_risk_score: 0.91 },
  },
  {
    forecast_id: 2,
    hotspot_id: 3,
    forecast_date: new Date().toISOString(),
    horizon_days: 7,
    predicted_eis: 88.0,
    predicted_risk_category: "High",
    confidence_lower: 82.0,
    confidence_upper: 92.0,
    top_features: { frequency_score: 0.84 },
  },
  {
    forecast_id: 3,
    hotspot_id: 1,
    forecast_date: new Date().toISOString(),
    horizon_days: 7,
    predicted_eis: 85.2,
    predicted_risk_category: "High",
    confidence_lower: 78.0,
    confidence_upper: 90.0,
    top_features: { density_score: 0.75 },
  },
];

export const mockAllocationLatest = {
  total_officers: 20,
  hotspots_covered: 4,
  unallocated_officers: 0,
  computed_at: new Date().toISOString(),
  allocations: [
    {
      id: 1,
      hotspot_id: 2,
      hotspot_name: "Jabalpur Railway Station",
      officers_allocated: 8,
      allocation_fraction: 0.4,
      priority_rank: 1,
      deployment_window: "Shift 2 (14:00 - 22:00)",
      eis_snapshot: 92.1,
      risk_category: "Critical",
      allocation_date: new Date().toISOString(),
    },
    {
      id: 2,
      hotspot_id: 1,
      hotspot_name: "Civic Center Junction",
      officers_allocated: 6,
      allocation_fraction: 0.3,
      priority_rank: 2,
      deployment_window: null,
      eis_snapshot: 78.4,
      risk_category: "High",
      allocation_date: new Date().toISOString(),
    },
    {
      id: 3,
      hotspot_id: 3,
      hotspot_name: "Gorakhpur Market Area",
      officers_allocated: 4,
      allocation_fraction: 0.2,
      priority_rank: 3,
      deployment_window: null,
      eis_snapshot: 81.5,
      risk_category: "High",
      allocation_date: new Date().toISOString(),
    },
    {
      id: 4,
      hotspot_id: 4,
      hotspot_name: "Sadar Cantt Road",
      officers_allocated: 2,
      allocation_fraction: 0.1,
      priority_rank: 4,
      deployment_window: null,
      eis_snapshot: 58.2,
      risk_category: "Medium",
      allocation_date: new Date().toISOString(),
    },
  ],
};

export const mockRoutingLatest = {
  route_id: 1,
  route_name: "Default Patrol",
  shift_label: "default",
  officer_count: 20,
  total_distance_km: 8.4,
  estimated_duration_min: 45,
  hotspots_covered: 4,
  total_eis_covered: 310.2,
  created_at: new Date().toISOString(),
  stops: [
    {
      sequence: 1,
      hotspot_id: 1,
      hotspot_name: "Civic Center Junction",
      latitude: 23.1678,
      longitude: 79.9322,
      risk_category: "High",
    },
    {
      sequence: 2,
      hotspot_id: 2,
      hotspot_name: "Jabalpur Railway Station",
      latitude: 23.1667,
      longitude: 79.95,
      risk_category: "Critical",
    },
    {
      sequence: 3,
      hotspot_id: 4,
      hotspot_name: "Sadar Cantt Road",
      latitude: 23.1492,
      longitude: 79.9489,
      risk_category: "Medium",
    },
    {
      sequence: 4,
      hotspot_id: 3,
      hotspot_name: "Gorakhpur Market Area",
      latitude: 23.1539,
      longitude: 79.9247,
      risk_category: "High",
    },
  ],
};

export function getMockResponse<T>(url: string, _params?: unknown): T {
  const cleanUrl = url.replace(/^\/?api\/v1\/?/, "").replace(/^\/?/, "").split("?")[0];

  if (cleanUrl === "dashboard/full") return mockDashboardFull as unknown as T;
  if (cleanUrl === "hotspots") return mockHotspots as unknown as T;
  if (cleanUrl === "eis/scores") return mockEisScores as unknown as T;
  if (cleanUrl === "forecast/summary") return mockForecastSummary as unknown as T;
  if (cleanUrl === "forecast/top") return mockForecastTop as unknown as T;
  if (cleanUrl === "allocation/latest") return mockAllocationLatest as unknown as T;
  if (cleanUrl === "routing/latest") return mockRoutingLatest as unknown as T;
  throw new Error(`Mock endpoint not found for URL: ${url}`);
}

export function getMockPostResponse<T>(url: string, body?: unknown): T {
  const cleanUrl = url.replace(/^\/?api\/v1\/?/, "").replace(/^\/?/, "").split("?")[0];
  void body;

  if (cleanUrl === "allocation/compute") return mockAllocationLatest as unknown as T;

  if (cleanUrl === "routing/generate") {
    return {
      route_id: 2,
      total_stops: 4,
      critical_stops: 1,
      high_stops: 2,
      total_distance_km: 8.4,
      estimated_travel_minutes: 25,
      estimated_total_minutes: 45,
      route_geometry: mockRoutingLatest.stops.map((s) => ({
        lat: s.latitude,
        lng: s.longitude,
      })),
      stops: mockRoutingLatest.stops,
    } as unknown as T;
  }

  if (cleanUrl === "forecast/generate") {
    return { status: "generated", forecasts_created: 4 } as unknown as T;
  }

  return { status: "success" } as unknown as T;
}
