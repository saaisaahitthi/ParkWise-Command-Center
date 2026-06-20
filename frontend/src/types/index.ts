// ── Shared API wrapper (optional legacy envelope) ──
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: "success" | "error";
}

export type { RiskChartSegment, DashboardView, ForecastSummaryView } from "./views";
export type * from "./backend";
export type * from "./views";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ── Risk levels ──
export type RiskLevel = "critical" | "high" | "medium" | "low";

// ── Zone ──
export interface Zone {
  id: string;
  name: string;
  district: string;
  lat: number;
  lng: number;
  violation_count: number;
  risk_score: number;
  risk_level: RiskLevel;
}

// ── Violation ──
export interface Violation {
  id: string;
  zone_id: string;
  zone_name: string;
  violation_type: string;
  timestamp: string;
  risk_score: number;
  risk_level: RiskLevel;
}

// ── Officer ──
export interface Officer {
  id: string;
  name: string;
  badge: string;
  zone_id: string;
  shift: "morning" | "afternoon" | "night";
  status: "on_duty" | "off_duty" | "responding";
}

// ── Forecast ──
export interface ForecastPoint {
  date: string;
  predicted: number;
  lower_ci: number;
  upper_ci: number;
  actual?: number;
}
