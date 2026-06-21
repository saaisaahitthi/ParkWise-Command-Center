import { useState } from "react";
import {
  AlertTriangle,
  MapPin,
  Navigation,
  ShieldCheck,
  Users,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { formatNumber } from "@/lib/utils";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RiskDonutChart } from "@/components/charts/RiskDonutChart";
import { MapMyIndiaWrapper } from "@/components/maps/MapMyIndiaWrapper";
import { PageHeader } from "@/layout/PageHeader";
import { useDashboard } from "@/hooks/useDashboard";
import {
  dashboardMetricDescriptions,
} from "@/data/dashboardPresentationData";

function latLngToXY(lat: number, lng: number) {
  const minLat = 12.80;
  const maxLat = 13.20;
  const minLng = 77.45;
  const maxLng = 77.80;

  const x = 20 + ((lng - minLng) / (maxLng - minLng)) * 60;
  const y = 80 - ((lat - minLat) / (maxLat - minLat)) * 60;

  return { x, y };
}

function mapRiskLevel(
  risk: string
): "Critical" | "High" | "Medium" | "Low" {
  return risk === "Critical" || risk === "High" || risk === "Medium"
    ? risk
    : "Low";
}

export default function DashboardPage() {
  const [selectedMarkerId, setSelectedMarkerId] = useState<string>("");

  const { data, isLoading, error } = useDashboard();

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />
          <p className="text-sm font-semibold">Streaming Command Telemetry...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto h-12 w-12 mb-3 text-red-500 animate-pulse" />
        <h3 className="text-lg font-semibold text-white">Dashboard temporarily unavailable</h3>
        <p className="mt-2 text-sm max-w-md mx-auto text-slate-400">
          We could not load the latest command-center metrics. Please try again shortly.
        </p>
      </div>
    );
  }

  const metricPresentation = {
    Violations: {
      description: dashboardMetricDescriptions.violations,
      icon: AlertTriangle,
      accent: "bg-[#F97316]/10 text-[#F97316]",
    },
    "Priority Zones": {
      description: dashboardMetricDescriptions.highRiskZones,
      icon: MapPin,
      accent: "bg-[#38BDF8]/10 text-[#38BDF8]",
    },
    "Officers on Duty": {
      description: dashboardMetricDescriptions.officersOnDuty,
      icon: Users,
      accent: "bg-[#10B981]/10 text-[#10B981]",
    },
    "Average Risk Score": {
      description: dashboardMetricDescriptions.averageRiskScore,
      icon: ShieldCheck,
      accent: "bg-[#A855F7]/10 text-[#A855F7]",
    },
  } as const;

  const priorityHotspots = data.hotspotMap.filter(
    (item) => item.displayRiskTier !== "Low"
  );
  const mapHotspots = priorityHotspots.slice(0, 20);
  const riskLegend = [
    { label: "Critical", color: "#EF4444" },
    { label: "High", color: "#F59E0B" },
    { label: "Medium", color: "#3B82F6" },
    { label: "Low", color: "#10B981" },
  ].filter((legend) =>
    mapHotspots.some((hotspot) => hotspot.displayRiskTier === legend.label)
  );

  const markers = mapHotspots.map((item) => {
    const { x, y } = latLngToXY(item.latitude, item.longitude);
    const color = item.displayRiskTier === "Critical"
      ? "#EF4444" 
      : item.displayRiskTier === "High"
        ? "#F59E0B" 
        : item.displayRiskTier === "Medium"
          ? "#3B82F6" 
          : "#10B981";
    return {
      id: String(item.hotspot_id),
      lat: item.latitude,
      lng: item.longitude,
      x,
      y,
      label: item.displayName,
      risk: mapRiskLevel(item.displayRiskTier),
      color,
      selected: String(item.hotspot_id) === selectedMarkerId,
    };
  });

  const selectedHotspot = priorityHotspots.find(
    (hotspot) => String(hotspot.hotspot_id) === selectedMarkerId
  );
  const popups = selectedHotspot
    ? [
        {
          id: `popup-${selectedHotspot.hotspot_id}`,
          title: selectedHotspot.displayName,
          description: `Risk Score: ${selectedHotspot.displayRiskScore.toFixed(1)} · Display Tier: ${selectedHotspot.displayRiskTier} · Rank: #${selectedHotspot.displayRiskRank}`,
          position: latLngToXY(selectedHotspot.latitude, selectedHotspot.longitude),
          latLng: [selectedHotspot.latitude, selectedHotspot.longitude] as [number, number],
          open: true,
        },
      ]
    : [];

  return (
    <div className="relative space-y-4">
      <div className="pointer-events-none absolute -left-20 -top-16 -z-10 h-72 w-72 rounded-full bg-cyan-400/[0.035] blur-3xl" />

      <PageHeader
        eyebrow="Command Overview"
        title="Dashboard"
        description="City-wide parking risk, enforcement capacity, and priority-zone status at a glance."
      />

      {/* KPIs Row */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {data.metrics.map((metric) => {
          const presentation =
            metricPresentation[
              metric.label as keyof typeof metricPresentation
            ] ?? metricPresentation["Average Risk Score"];
          return (
            <MetricCard
              key={metric.label}
              label={metric.label}
              value={
                typeof metric.value === "number"
                  ? formatNumber(metric.value)
                  : metric.value
              }
              delta={metric.delta}
              description={presentation.description}
              icon={presentation.icon}
              accent={presentation.accent}
            />
          );
        })}
      </div>

      {/* Main Content Layout */}
      <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,2.05fr)_minmax(310px,0.95fr)]">
        {/* Map */}
        <div className="dashboard-map-shell rounded-[28px] border border-cyan-300/10 bg-slate-950/50 p-1.5 shadow-[0_35px_90px_-55px_rgba(34,211,238,0.65)]">
          <MapMyIndiaWrapper
            title="Bengaluru Command Map"
            subtitle="Showing top 20 priority hotspots across Bengaluru"
            markers={markers}
            popups={popups}
            legendItems={riskLegend}
            onMarkerClick={(marker) => setSelectedMarkerId(marker.id)}
            variant="dashboard"
          />
        </div>

        {/* Executive command stack */}
        <div className="grid gap-3">
          <Card className="rounded-[22px] border-white/[0.07] bg-[linear-gradient(145deg,rgba(14,27,39,0.92),rgba(8,17,27,0.8))] p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-white">
                  Risk Distribution
                </h3>
                <p className="mt-0.5 text-[10px] text-slate-500">
                  Current city-wide exposure mix
                </p>
              </div>
              <ShieldCheck className="h-4 w-4 text-cyan-300/70" />
            </div>
            <RiskDonutChart data={data.riskChart} />
          </Card>

          <Card className="overflow-hidden rounded-[22px] border-white/[0.07] bg-[linear-gradient(145deg,rgba(14,27,39,0.92),rgba(8,17,27,0.8))] p-0">
            <div className="flex items-center justify-between border-b border-white/[0.06] px-4 py-3">
              <div>
                <h3 className="text-sm font-semibold text-white">
                  Top Priority Hotspots
                </h3>
                <p className="mt-0.5 text-[10px] text-slate-500">
                  Top ranked hotspots by risk score across the city
                </p>
              </div>
              <MapPin className="h-4 w-4 text-rose-300/80" />
            </div>
            <div className="max-h-[220px] space-y-1 overflow-y-auto p-2">
              {priorityHotspots.slice(0, 5).map((hotspot) => (
                <button
                  type="button"
                  key={hotspot.hotspot_id}
                  onClick={() =>
                    setSelectedMarkerId(String(hotspot.hotspot_id))
                  }
                  className={`flex w-full items-center justify-between gap-3 rounded-xl border px-3 py-2.5 text-left transition duration-200 hover:border-white/[0.08] hover:bg-white/[0.04] ${
                    String(hotspot.hotspot_id) === selectedMarkerId
                      ? "border-cyan-300/12 bg-cyan-300/[0.06]"
                      : "border-transparent"
                  }`}
                >
                  <div className="min-w-0">
                    <p className="truncate text-xs font-semibold text-slate-200">
                      {hotspot.displayName}
                    </p>
                    <p className="mt-0.5 flex items-center gap-1 text-[10px] text-slate-500">
                      <Navigation className="h-2.5 w-2.5" />
                      {hotspot.hotspot_type !== "Unknown"
                        ? hotspot.hotspot_type
                        : hotspot.displaySubtext}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 rounded-full border px-2 py-1 text-[9px] font-bold uppercase tracking-wider ${
                      hotspot.displayRiskTier === "Critical"
                        ? "border-rose-400/20 bg-rose-400/[0.09] text-rose-200"
                        : hotspot.displayRiskTier === "High"
                          ? "border-amber-300/20 bg-amber-300/[0.08] text-amber-200"
                          : "border-sky-300/20 bg-sky-300/[0.08] text-sky-200"
                    }`}
                  >
                    {hotspot.displayRiskTier}
                  </span>
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
