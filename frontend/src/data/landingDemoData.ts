export const USE_LANDING_MOCK_FALLBACK = true;

export type LandingRiskLevel = "critical" | "high" | "medium";

export type LandingLayerIcon =
  | "critical"
  | "risk"
  | "route"
  | "officers"
  | "forecast";

export interface LandingNavItem {
  label: string;
  path: string;
}

export interface LandingMapLayer {
  label: string;
  detail: string;
  icon: LandingLayerIcon;
  color: string;
}

export interface LandingStat {
  value: string;
  label: string;
}

export interface LandingHotspotMarker {
  label: string;
  left: string;
  top: string;
  level: LandingRiskLevel;
}

export interface SelectedLandingHotspot {
  eyebrow: string;
  title: string;
  location: string;
  risk: string;
  suggestedAction: string;
  route: string;
}

export interface LandingOverviewData {
  navigation: LandingNavItem[];
  hero: {
    eyebrow: string;
    title: string;
    highlightedTitle: string;
    subtitle: string;
  };
  workflow: string[];
  mapLayers: LandingMapLayer[];
  hotspots: LandingHotspotMarker[];
  selectedHotspot: SelectedLandingHotspot;
  stats: LandingStat[];
}

/**
 * Presentation fallback for the landing page.
 *
 * When a confirmed landing-overview API contract is available, map its response
 * into LandingOverviewData and fall back to this object for missing data. Keep
 * endpoint access inside the existing services/hooks layer rather than here.
 */
export const landingDemoData: LandingOverviewData = {
  navigation: [
    { label: "Dashboard", path: "/dashboard" },
    { label: "Hotspots", path: "/hotspots" },
    { label: "Risk Score", path: "/temporal" },
    { label: "Forecast", path: "/forecast" },
    { label: "Allocation", path: "/officers" },
    { label: "Patrol", path: "/patrol" },
  ],
  hero: {
    eyebrow: "Bengaluru Parking Intelligence",
    title: "Smarter Parking & Congestion",
    highlightedTitle: "Command Center",
    subtitle:
      "Detect parking-induced congestion hotspots, predict future risk, allocate enforcement units, and generate optimized patrol routes.",
  },
  workflow: ["Detect", "Analyze", "Allocate", "Route"],
  mapLayers: [
    {
      label: "Critical Zones",
      detail: "12 active",
      icon: "critical",
      color: "text-rose-300",
    },
    {
      label: "High Risk",
      detail: "28 monitored",
      icon: "risk",
      color: "text-amber-300",
    },
    {
      label: "Patrol Routes",
      detail: "9 optimized",
      icon: "route",
      color: "text-cyan-300",
    },
    {
      label: "Officer Units",
      detail: "46 available",
      icon: "officers",
      color: "text-emerald-300",
    },
    {
      label: "Forecast Risk",
      detail: "Next 24 hours",
      icon: "forecast",
      color: "text-violet-300",
    },
  ],
  hotspots: [
    {
      label: "Railway Station",
      left: "24%",
      top: "38%",
      level: "critical",
    },
    { label: "MG Road", left: "47%", top: "29%", level: "high" },
    { label: "KR Market", left: "58%", top: "57%", level: "critical" },
    { label: "Metro Exit", left: "72%", top: "34%", level: "medium" },
    {
      label: "Commercial Street",
      left: "80%",
      top: "68%",
      level: "high",
    },
  ],
  selectedHotspot: {
    eyebrow: "Critical Hotspot",
    title: "Railway Station Zone",
    location: "Railway Station Zone",
    risk: "Critical",
    suggestedAction: "Deploy 5 officers",
    route: "Patrol Route 03",
  },
  stats: [
    { value: "2,98,450", label: "Violations Analyzed" },
    { value: "5,872", label: "Hotspots Detected" },
    { value: "13,032", label: "Peak Windows" },
    { value: "R² 0.87", label: "Forecast Performance" },
  ],
};

export function resolveLandingOverviewData(
  apiData?: LandingOverviewData
): LandingOverviewData {
  if (apiData) {
    return apiData;
  }

  if (USE_LANDING_MOCK_FALLBACK) {
    return landingDemoData;
  }

  throw new Error("Landing overview data is unavailable.");
}
