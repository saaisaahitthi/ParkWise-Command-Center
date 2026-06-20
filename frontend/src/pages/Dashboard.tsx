import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, MapPin, ShieldCheck, Users } from "lucide-react";
import { Card } from "@/components/ui/card";
import { formatNumber } from "@/lib/utils";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RiskDonutChart } from "@/components/charts/RiskDonutChart";
import { MapMyIndiaWrapper } from "@/components/maps/MapMyIndiaWrapper";
import { apiGet } from "@/lib/api";

// Map Jabalpur coordinates to mock SVG coordinates (0 - 100) for visual representation
function latLngToXY(lat: number, lng: number) {
  const minLat = 23.14;
  const maxLat = 23.18;
  const minLng = 79.92;
  const maxLng = 79.96;

  const x = 20 + ((lng - minLng) / (maxLng - minLng)) * 60;
  const y = 80 - ((lat - minLat) / (maxLat - minLat)) * 60;

  return { x, y };
}

export default function DashboardPage() {
  const [selectedMarkerId, setSelectedMarkerId] = useState<string>("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard-full"],
    queryFn: () => apiGet<any>("/dashboard/full"),
    refetchInterval: 10000,
  });

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

  const { executive_summary, risk_distribution, hotspot_map } = data;

  const metrics = [
    {
      label: "Violations",
      value: executive_summary.total_violations,
      delta: `+${executive_summary.total_violations_delta}%`,
      icon: AlertTriangle,
      accent: "bg-[#F97316]/10 text-[#F97316]",
    },
    {
      label: "High Risk Zones",
      value: executive_summary.high_risk_zones,
      delta: `+${executive_summary.high_risk_zones_delta}%`,
      icon: MapPin,
      accent: "bg-[#38BDF8]/10 text-[#38BDF8]",
    },
    {
      label: "Officers on Duty",
      value: executive_summary.officers_on_duty,
      delta: "",
      icon: Users,
      accent: "bg-[#10B981]/10 text-[#10B981]",
    },
    {
      label: "Average Risk Score",
      value: executive_summary.avg_risk_score,
      delta: "",
      icon: ShieldCheck,
      accent: "bg-[#A855F7]/10 text-[#A855F7]",
    },
  ];

  const markers = hotspot_map.map((item: any) => {
    const { x, y } = latLngToXY(item.latitude, item.longitude);
    const color = item.risk_category === "Critical" 
      ? "#EF4444" 
      : item.risk_category === "High" 
        ? "#F59E0B" 
        : item.risk_category === "Medium" 
          ? "#3B82F6" 
          : "#10B981";
    return {
      id: item.hotspot_id,
      lat: item.latitude,
      lng: item.longitude,
      x,
      y,
      label: item.name,
      risk: item.risk_category,
      color,
      selected: item.hotspot_id === selectedMarkerId,
    };
  });

  const selectedHotspot = hotspot_map.find((h: any) => h.hotspot_id === selectedMarkerId);
  const popups = selectedHotspot
    ? [
        {
          id: `popup-${selectedHotspot.hotspot_id}`,
          title: selectedHotspot.name,
          description: `EIS: ${selectedHotspot.latest_eis} • Forecast EIS: ${selectedHotspot.forecasted_eis} • Risk: ${selectedHotspot.risk_category} • Officers: ${selectedHotspot.officers_allocated}`,
          position: latLngToXY(selectedHotspot.latitude, selectedHotspot.longitude),
          latLng: [selectedHotspot.latitude, selectedHotspot.longitude] as [number, number],
          open: true,
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* KPIs Row */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <MetricCard
            key={metric.label}
            label={metric.label}
            value={typeof metric.value === "number" ? formatNumber(metric.value) : metric.value}
            delta={metric.delta}
            icon={metric.icon}
            accent={metric.accent}
          />
        ))}
      </div>

      {/* Main Content Layout */}
      <div className="grid gap-6 xl:grid-cols-[1.8fr_0.9fr]">
        {/* Map */}
        <MapMyIndiaWrapper
          title="Command Center Map - Bengaluru"
          subtitle="Interactive visual representation of risk zones and patrol areas"
          markers={markers}
          popups={popups}
          legendItems={[
            { label: "Critical Risk", color: "#EF4444" },
            { label: "High Risk", color: "#F59E0B" },
            { label: "Medium Risk", color: "#3B82F6" },
            { label: "Low Risk", color: "#10B981" },
          ]}
          onMarkerClick={(marker) => setSelectedMarkerId(marker.id)}
        />

        {/* Side Panel: Risk Donut & Top Hotspots List */}
        <div className="space-y-6">
          <Card className="rounded-[32px] border border-[var(--color-card-border)] bg-[var(--color-card-bg)] p-6">
            <h3 className="text-md font-semibold text-white mb-4">Risk Distribution</h3>
            <RiskDonutChart data={risk_distribution} />
          </Card>

          <Card className="rounded-[32px] border border-[var(--color-card-border)] bg-[var(--color-card-bg)] p-6 space-y-4">
            <h3 className="text-md font-semibold text-white">Active Hotspots</h3>
            <div className="divide-y divide-slate-800">
              {hotspot_map.map((hotspot: any) => (
                <div
                  key={hotspot.hotspot_id}
                  onClick={() => setSelectedMarkerId(hotspot.hotspot_id)}
                  className={`py-3 flex items-center justify-between cursor-pointer transition-colors hover:bg-slate-900/40 rounded-xl px-2 ${
                    hotspot.hotspot_id === selectedMarkerId ? "bg-slate-900/60" : ""
                  }`}
                >
                  <div>
                    <p className="text-sm font-medium text-slate-200">{hotspot.name}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{hotspot.hotspot_type}</p>
                  </div>
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-semibold border ${
                      hotspot.risk_category === "Critical"
                        ? "border-red-900 bg-red-950/40 text-red-300"
                        : hotspot.risk_category === "High"
                          ? "border-amber-900 bg-amber-950/40 text-amber-300"
                          : "border-blue-900 bg-blue-950/40 text-blue-300"
                    }`}
                  >
                    {hotspot.risk_category}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
