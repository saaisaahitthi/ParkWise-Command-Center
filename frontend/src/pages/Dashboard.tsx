import { useState } from "react";
import { AlertTriangle, MapPin, ShieldCheck, Users } from "lucide-react";
import { Card } from "@/components/ui/card";
import { formatNumber } from "@/lib/utils";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { RiskDonutChart } from "@/components/charts/RiskDonutChart";
import { MapMyIndiaWrapper } from "@/components/maps/MapMyIndiaWrapper";
import { useDashboard } from "@/hooks/useDashboard";

function latLngToXY(lat: number, lng: number) {
  const minLat = 23.14;
  const maxLat = 23.18;
  const minLng = 79.92;
  const maxLng = 79.96;

  const x = 20 + ((lng - minLng) / (maxLng - minLng)) * 60;
  const y = 80 - ((lat - minLat) / (maxLat - minLat)) * 60;

  return { x, y };
}

const METRIC_ICONS = [AlertTriangle, MapPin, Users, ShieldCheck] as const;
const METRIC_ACCENTS = [
  "bg-[#F97316]/10 text-[#F97316]",
  "bg-[#38BDF8]/10 text-[#38BDF8]",
  "bg-[#10B981]/10 text-[#10B981]",
  "bg-[#A855F7]/10 text-[#A855F7]",
] as const;

export default function DashboardPage() {
  const [selectedMarkerId, setSelectedMarkerId] = useState<number | null>(null);
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
        <h3 className="text-lg font-semibold text-white">Data Stream Disconnected</h3>
        <p className="mt-2 text-sm max-w-md mx-auto text-slate-400">
          Unable to fetch dashboard metrics. Please verify that the local backend service at{" "}
          <code className="text-red-200">http://127.0.0.1:8000/api/v1</code> is running, or toggle
          the header mode to Mock Simulation.
        </p>
      </div>
    );
  }

 const { metrics, riskChart } = data;
const hotspotMap = data.hotspotMap.slice(0, 50);

  const markers = hotspotMap.map((item) => {
    const { x, y } = latLngToXY(item.latitude, item.longitude);
    const color =
      item.risk_category === "Critical"
        ? "#EF4444"
        : item.risk_category === "High"
          ? "#F59E0B"
          : item.risk_category === "Medium"
            ? "#3B82F6"
            : "#10B981";
    return {
      id: String(item.hotspot_id),
      lat: item.latitude,
      lng: item.longitude,
      x,
      y,
      label: item.name,
      risk: item.risk_category as "Critical" | "High" | "Medium" | "Low",
      color,
      selected: item.hotspot_id === selectedMarkerId,
    };
  });

  const selectedHotspot = hotspotMap.find((h) => h.hotspot_id === selectedMarkerId);
  const popups = selectedHotspot
    ? [
        {
          id: `popup-${selectedHotspot.hotspot_id}`,
          title: selectedHotspot.name,
          description: `EIS: ${selectedHotspot.latest_eis ?? "—"} • Forecast EIS: ${selectedHotspot.forecasted_eis ?? "—"} • Risk: ${selectedHotspot.risk_category} • Officers: ${selectedHotspot.officers_allocated ?? 0}`,
          position: latLngToXY(selectedHotspot.latitude, selectedHotspot.longitude),
          latLng: [selectedHotspot.latitude, selectedHotspot.longitude] as [number, number],
          open: true,
        },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric, index) => (
          <MetricCard
            key={metric.label}
            label={metric.label}
            value={typeof metric.value === "number" ? formatNumber(metric.value) : metric.value}
            delta={metric.delta}
            icon={METRIC_ICONS[index]}
            accent={METRIC_ACCENTS[index]}
          />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.8fr_0.9fr]">
        <MapMyIndiaWrapper
          title="Command Center Map - Jabalpur"
          subtitle="Interactive visual representation of risk zones and patrol areas"
          markers={markers}
          popups={popups}
          legendItems={[
            { label: "Critical Risk", color: "#EF4444" },
            { label: "High Risk", color: "#F59E0B" },
            { label: "Medium Risk", color: "#3B82F6" },
            { label: "Low Risk", color: "#10B981" },
          ]}
          onMarkerClick={(marker) => setSelectedMarkerId(Number(marker.id))}
        />

        <div className="space-y-6">
          <Card className="rounded-[32px] border border-[var(--color-card-border)] bg-[var(--color-card-bg)] p-6">
            <h3 className="text-md font-semibold text-white mb-4">Risk Distribution</h3>
            <RiskDonutChart data={riskChart} />
          </Card>

          <Card className="rounded-[32px] border border-[var(--color-card-border)] bg-[var(--color-card-bg)] p-6 space-y-4">
            <h3 className="text-md font-semibold text-white">Active Hotspots</h3>
            <div className="divide-y divide-slate-800">
              {hotspotMap.map((hotspot) => (
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
