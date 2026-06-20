// Mock data representing Jabalpur Command Center telemetry

export const mockDashboardFull = {
  executive_summary: {
    total_violations: 298450,
    total_violations_delta: 5.8,
    high_risk_zones: 4,
    high_risk_zones_delta: 12.1,
    officers_on_duty: 20,
    avg_risk_score: 75.3,
  },
  risk_distribution: [
    { name: "Critical", value: 1, color: "#EF4444" },
    { name: "High", value: 2, color: "#F59E0B" },
    { name: "Medium", value: 1, color: "#3B82F6" },
  ],
  hotspot_map: [
    {
      hotspot_id: "hotspot-civic-center",
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
      hotspot_id: "hotspot-railway-station",
      name: "Jabalpur Railway Station",
      latitude: 23.1667,
      longitude: 79.9500,
      hotspot_type: "Transit Node",
      violation_count: 703,
      latest_eis: 92.1,
      risk_category: "Critical",
      forecasted_eis: 94.5,
      officers_allocated: 8,
    },
    {
      hotspot_id: "hotspot-gorakhpur",
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
      hotspot_id: "hotspot-sadar",
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
};

export const mockHotspots = {
  items: [
    {
      hotspot_name: "Jabalpur Railway Station",
      total_violations: 703,
      dominant_violation_type: "No Parking Zone",
      dominant_vehicle_category: "Auto-Rickshaw",
      unique_dates: 30,
      centroid_lat: 23.1667,
      centroid_lon: 79.9500,
    },
    {
      hotspot_name: "Gorakhpur Market Area",
      total_violations: 558,
      dominant_violation_type: "Obstruction",
      dominant_vehicle_category: "Four-Wheeler",
      unique_dates: 25,
      centroid_lat: 23.1539,
      centroid_lon: 79.9247,
    },
    {
      hotspot_name: "Civic Center Junction",
      total_violations: 482,
      dominant_violation_type: "Double Parking",
      dominant_vehicle_category: "Two-Wheeler",
      unique_dates: 28,
      centroid_lat: 23.1678,
      centroid_lon: 79.9322,
    },
    {
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

export const mockEisScores = [
  {
    rank: 1,
    hotspot_id: "hotspot-railway-station",
    eis_score: 92.1,
    risk_category: "Critical",
    frequency_score: 0.95,
    recurrence_score: 0.92,
    density_score: 0.88,
    temporal_risk_score: 0.91,
    severity_norm: 0.85,
    exposure_score: 0.90,
    severity_multiplier: 1.2,
  },
  {
    rank: 2,
    hotspot_id: "hotspot-gorakhpur",
    eis_score: 81.5,
    risk_category: "High",
    frequency_score: 0.84,
    recurrence_score: 0.81,
    density_score: 0.78,
    temporal_risk_score: 0.82,
    severity_norm: 0.75,
    exposure_score: 0.80,
    severity_multiplier: 1.15,
  },
  {
    rank: 3,
    hotspot_id: "hotspot-civic-center",
    eis_score: 78.4,
    risk_category: "High",
    frequency_score: 0.82,
    recurrence_score: 0.79,
    density_score: 0.75,
    temporal_risk_score: 0.80,
    severity_norm: 0.72,
    exposure_score: 0.78,
    severity_multiplier: 1.1,
  },
  {
    rank: 4,
    hotspot_id: "hotspot-sadar",
    eis_score: 58.2,
    risk_category: "Medium",
    frequency_score: 0.60,
    recurrence_score: 0.58,
    density_score: 0.55,
    temporal_risk_score: 0.62,
    severity_norm: 0.50,
    exposure_score: 0.56,
    severity_multiplier: 1.0,
  },
];

export const mockForecastSummary = {
  forecast_horizon: "7 Days",
  predicted_high_risk_hotspots: 3,
  avg_predicted_eis: 75.3,
};

export const mockForecastTop = [
  {
    hotspot_id: "hotspot-railway-station",
    name: "Jabalpur Railway Station",
    current_eis: 92.1,
    forecasted_eis: 94.5,
    risk_category: "Critical",
    action_recommended: "Increase patrol density during morning peak (8-10 AM)",
  },
  {
    hotspot_id: "hotspot-gorakhpur",
    name: "Gorakhpur Market Area",
    current_eis: 81.5,
    forecasted_eis: 88.0,
    risk_category: "High",
    action_recommended: "Deploy additional 2 officers for evening peak (5-7 PM)",
  },
  {
    hotspot_id: "hotspot-civic-center",
    name: "Civic Center Junction",
    current_eis: 78.4,
    forecasted_eis: 85.2,
    risk_category: "High",
    action_recommended: "Ensure active signage at commercial parking entry",
  },
];

export const mockAllocationLatest = {
  total_officers_allocated: 20,
  hotspots_covered: 4,
  deployment_window: "Shift 2 (14:00 - 22:00)",
  allocations: [
    {
      hotspot_name: "Jabalpur Railway Station",
      officers_allocated: 8,
      risk_category: "Critical",
      priority: 1,
    },
    {
      hotspot_name: "Civic Center Junction",
      officers_allocated: 6,
      risk_category: "High",
      priority: 2,
    },
    {
      hotspot_name: "Gorakhpur Market Area",
      officers_allocated: 4,
      risk_category: "High",
      priority: 3,
    },
    {
      hotspot_name: "Sadar Cantt Road",
      officers_allocated: 2,
      risk_category: "Medium",
      priority: 4,
    },
  ],
};

export const mockRoutingLatest = {
  route_id: "route-01",
  total_stops: 4,
  critical_high_stops: 3,
  total_distance_km: 8.4,
  estimated_travel_time_minutes: 45,
  route_geometry: [
    { lat: 23.1678, lng: 79.9322 },
    { lat: 23.1667, lng: 79.9500 },
    { lat: 23.1492, lng: 79.9489 },
    { lat: 23.1539, lng: 79.9247 },
  ],
  stop_sequence: [
    { sequence: 1, name: "Civic Center Junction", risk: "High" },
    { sequence: 2, name: "Jabalpur Railway Station", risk: "Critical" },
    { sequence: 3, name: "Sadar Cantt Road", risk: "Medium" },
    { sequence: 4, name: "Gorakhpur Market Area", risk: "High" },
  ],
};

export function getMockResponse<T>(url: string, params?: unknown): T {
  void params;
  const cleanUrl = url.replace(/^\/?api\/v1\/?/, "").replace(/^\/?/, "").split("?")[0];

  if (cleanUrl === "dashboard/full") {
    return mockDashboardFull as unknown as T;
  }
  if (cleanUrl === "hotspots") {
    return mockHotspots as unknown as T;
  }
  if (cleanUrl === "eis/scores") {
    return mockEisScores as unknown as T;
  }
  if (cleanUrl === "forecast/summary") {
    return mockForecastSummary as unknown as T;
  }
  if (cleanUrl === "forecast/top") {
    return mockForecastTop as unknown as T;
  }
  if (cleanUrl === "allocation/latest" || cleanUrl === "dashboard/allocation") {
    return mockAllocationLatest as unknown as T;
  }
  if (cleanUrl === "routing/latest" || cleanUrl === "routing/summary" || cleanUrl === "patrol/") {
    return mockRoutingLatest as unknown as T;
  }
  throw new Error(`Mock endpoint not found for URL: ${url}`);
}

export function getMockPostResponse<T>(url: string, body?: unknown): T {
  void body;
  const cleanUrl = url.replace(/^\/?api\/v1\/?/, "").replace(/^\/?/, "").split("?")[0];

  if (cleanUrl === "allocation/compute") {
    return {
      status: "success",
      message: "Resource allocation recomputed successfully.",
      computed_allocation: mockAllocationLatest,
    } as unknown as T;
  }

  if (cleanUrl === "routing/generate") {
    return {
      status: "success",
      message: "Route geometry re-routed successfully.",
      route: mockRoutingLatest,
    } as unknown as T;
  }

  return { status: "success", message: "Mock operation completed." } as unknown as T;
}
