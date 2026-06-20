import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  CarFront,
  ChevronLeft,
  ChevronRight,
  Crosshair,
  Layers3,
  Search,
} from "lucide-react";
import { MapMyIndiaWrapper } from "@/components/maps/MapMyIndiaWrapper";
import { Card } from "@/components/ui/card";
import { getLocationDisplayName } from "@/data/dashboardPresentationData";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/layout/PageHeader";

interface HotspotRecord {
  hotspot_name: string;
  centroid_lat: number;
  centroid_lon: number;
  total_violations: number;
  dominant_violation_type: string;
  dominant_vehicle_category: string;
  unique_dates: number;
}

interface HotspotListResponse {
  items: HotspotRecord[];
  total: number;
  page_size: number;
}

type HotspotRisk = "Critical" | "High" | "Medium";

const numberFormatter = new Intl.NumberFormat("en-IN");

function latLngToXY(lat: number, lng: number) {
  const minLat = 23.14;
  const maxLat = 23.18;
  const minLng = 79.92;
  const maxLng = 79.96;

  const x = 20 + ((lng - minLng) / (maxLng - minLng)) * 60;
  const y = 80 - ((lat - minLat) / (maxLat - minLat)) * 60;

  return { x, y };
}

function getHotspotRisk(totalViolations: number): HotspotRisk {
  if (totalViolations >= 650) return "Critical";
  if (totalViolations >= 450) return "High";
  return "Medium";
}

function getRiskColor(risk: HotspotRisk) {
  if (risk === "Critical") return "#EF4444";
  if (risk === "High") return "#F59E0B";
  return "#3B82F6";
}

function getRiskClasses(risk: HotspotRisk) {
  if (risk === "Critical") {
    return "border-rose-400/20 bg-rose-400/10 text-rose-200";
  }
  if (risk === "High") {
    return "border-amber-400/20 bg-amber-400/10 text-amber-200";
  }
  return "border-blue-400/20 bg-blue-400/10 text-blue-200";
}

export default function HotspotsPage() {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [minViolations, setMinViolations] = useState(0);
  const [selectedHotspotName, setSelectedHotspotName] = useState("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["hotspots", page, minViolations],
    queryFn: () =>
      apiGet<HotspotListResponse>(
        `/hotspots?page=${page}&page_size=10&min_violations=${minViolations}`
      ),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />
          <p className="text-sm font-semibold">Loading hotspot intelligence…</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto mb-3 h-12 w-12 text-red-500" />
        <h3 className="text-lg font-semibold text-white">
          Hotspot data is unavailable
        </h3>
        <p className="mt-2 text-sm text-slate-400">
          The current hotspot records could not be loaded. Please check the
          service connection and try again.
        </p>
      </div>
    );
  }

  const { items = [], total = 0, page_size = 10 } = data;
  const normalizedSearch = searchQuery.trim().toLowerCase();
  const filteredItems = items.filter((item) =>
    item.hotspot_name.toLowerCase().includes(normalizedSearch)
  );

  const markers = filteredItems.map((item) => {
    const { x, y } = latLngToXY(item.centroid_lat, item.centroid_lon);
    const risk = getHotspotRisk(item.total_violations);

    return {
      id: item.hotspot_name,
      lat: item.centroid_lat,
      lng: item.centroid_lon,
      x,
      y,
      label: getLocationDisplayName(item.hotspot_name),
      risk,
      color: getRiskColor(risk),
      selected: item.hotspot_name === selectedHotspotName,
    };
  });

  const selectedHotspot =
    filteredItems.find(
      (hotspot) => hotspot.hotspot_name === selectedHotspotName
    ) ?? filteredItems[0];

  const popups =
    selectedHotspot &&
    selectedHotspot.hotspot_name === selectedHotspotName
      ? [
          {
            id: `popup-${selectedHotspot.hotspot_name}`,
            title: getLocationDisplayName(selectedHotspot.hotspot_name),
            description: `Total Violations: ${selectedHotspot.total_violations} | Dominant: ${selectedHotspot.dominant_violation_type} (${selectedHotspot.dominant_vehicle_category})`,
            position: latLngToXY(
              selectedHotspot.centroid_lat,
              selectedHotspot.centroid_lon
            ),
            latLng: [
              selectedHotspot.centroid_lat,
              selectedHotspot.centroid_lon,
            ] as [number, number],
            open: true,
          },
        ]
      : [];

  const totalPages = Math.max(1, Math.ceil(total / page_size));

  return (
    <div className="space-y-4 pb-6">
      <PageHeader
        eyebrow="Spatial Intelligence"
        title="Hotspot Intelligence"
        description="Filter, inspect, and compare detected parking-congestion clusters across Bengaluru."
      />

      <div className="grid items-start gap-5 xl:grid-cols-[280px_minmax(0,1fr)]">
        <Card className="relative h-fit overflow-hidden rounded-[24px] border-cyan-300/[0.1] bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.1),transparent_38%),linear-gradient(150deg,rgba(14,27,39,0.96),rgba(7,15,24,0.9))] p-4 shadow-[0_24px_70px_-50px_rgba(34,211,238,0.9)]">
          <div className="pointer-events-none absolute -right-12 -top-12 h-28 w-28 rounded-full border border-cyan-300/[0.08]" />
          <div className="relative">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-300/15 bg-cyan-300/[0.07] text-cyan-200">
              <Crosshair className="h-4 w-4" />
            </span>
            <p className="mt-4 text-[9px] font-semibold uppercase tracking-[0.24em] text-cyan-300/70">
              Investigation Controls
            </p>
            <h2 className="mt-1 text-base font-semibold text-white">
              Filter hotspots
            </h2>
            <p className="mt-1.5 text-xs leading-5 text-slate-500">
              Narrow the current records by location name and minimum violation
              volume.
            </p>
          </div>

          <div className="relative mt-5 space-y-5">
            <label className="block">
              <span className="mb-2 block text-[11px] font-semibold text-slate-300">
                Search area
              </span>
              <span className="relative block">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search hotspot…"
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                  className="w-full rounded-xl border border-white/[0.08] bg-black/25 py-2.5 pl-9 pr-3 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300/35 focus:ring-2 focus:ring-cyan-300/[0.06]"
                />
              </span>
            </label>

            <label className="block">
              <span className="flex items-center justify-between gap-3 text-[11px] font-semibold text-slate-300">
                Minimum violations
                <span className="rounded-lg border border-cyan-300/15 bg-cyan-300/[0.06] px-2 py-1 font-mono text-cyan-200">
                  {numberFormatter.format(minViolations)}
                </span>
              </span>
              <input
                type="range"
                min="0"
                max="800"
                step="50"
                value={minViolations}
                onChange={(event) => {
                  setMinViolations(Number(event.target.value));
                  setPage(1);
                }}
                className="mt-3 h-1.5 w-full cursor-pointer accent-cyan-300"
              />
            </label>

            <div className="grid grid-cols-2 gap-2 border-t border-white/[0.07] pt-4">
              <div className="rounded-xl border border-white/[0.06] bg-black/20 p-3">
                <p className="text-[9px] uppercase tracking-[0.14em] text-slate-600">
                  Visible
                </p>
                <p className="mt-1 font-mono text-lg font-bold text-white">
                  {filteredItems.length}
                </p>
              </div>
              <div className="rounded-xl border border-white/[0.06] bg-black/20 p-3">
                <p className="text-[9px] uppercase tracking-[0.14em] text-slate-600">
                  Total records
                </p>
                <p className="mt-1 font-mono text-lg font-bold text-white">
                  {numberFormatter.format(total)}
                </p>
              </div>
            </div>
          </div>
        </Card>

        <div className="hotspot-map-shell rounded-[28px] border border-cyan-300/10 bg-slate-950/50 p-1.5 shadow-[0_35px_90px_-55px_rgba(34,211,238,0.65)]">
          <MapMyIndiaWrapper
            title="Spatial Hotspot Distribution"
            subtitle="Select a map marker or table record to inspect its congestion centroid."
            markers={markers}
            popups={popups}
            legendItems={[
              { label: "Critical ≥650", color: "#EF4444" },
              { label: "High 450–649", color: "#F59E0B" },
              { label: "Medium <450", color: "#3B82F6" },
            ]}
            onMarkerClick={(marker) => setSelectedHotspotName(marker.id)}
            variant="dashboard"
          />
        </div>
      </div>

      <Card className="overflow-hidden rounded-[26px] border-cyan-300/[0.08] bg-[linear-gradient(145deg,rgba(14,27,39,0.94),rgba(8,17,27,0.84))] p-0 shadow-[0_28px_80px_-58px_rgba(34,211,238,0.6)]">
        <div className="flex flex-col gap-3 border-b border-white/[0.06] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-[9px] font-semibold uppercase tracking-[0.2em] text-cyan-300/65">
              Cluster database
            </p>
            <h2 className="mt-1 text-sm font-semibold text-white">
              Hotspot Records
            </h2>
            <p className="mt-0.5 text-[10px] text-slate-500">
              Spatial and violation attributes for the currently loaded page
            </p>
          </div>
          <span className="flex w-fit items-center gap-2 rounded-full border border-white/[0.07] bg-black/20 px-3 py-1.5 text-[10px] text-slate-400">
            <Layers3 className="h-3.5 w-3.5 text-cyan-300" />
            {filteredItems.length} visible
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="border-b border-white/[0.06] bg-black/15 text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
                <th className="px-4 py-3">Hotspot</th>
                <th className="px-4 py-3 text-center">Risk</th>
                <th className="px-4 py-3 text-right">Violations</th>
                <th className="px-4 py-3">Dominant violation</th>
                <th className="px-4 py-3">Vehicle</th>
                <th className="px-4 py-3 text-center">Active days</th>
                <th className="px-4 py-3 text-right">Coordinates</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.055] text-sm text-slate-300">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-slate-500">
                    No hotspots match the current filters.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => {
                  const risk = getHotspotRisk(item.total_violations);
                  const isSelected =
                    item.hotspot_name === selectedHotspotName;

                  return (
                    <tr
                      key={item.hotspot_name}
                      onClick={() => setSelectedHotspotName(item.hotspot_name)}
                      className={`cursor-pointer transition duration-200 hover:bg-cyan-300/[0.035] ${
                        isSelected
                          ? "bg-cyan-300/[0.055] text-white"
                          : ""
                      }`}
                    >
                      <td className="px-4 py-3.5">
                        <div className="flex items-center gap-3">
                          <span
                            className={`h-2 w-2 shrink-0 rounded-full shadow-[0_0_10px_currentColor] ${
                              risk === "Critical"
                                ? "text-rose-400"
                                : risk === "High"
                                  ? "text-amber-400"
                                  : "text-blue-400"
                            }`}
                            style={{ backgroundColor: "currentColor" }}
                          />
                          <span className="font-medium text-slate-200">
                            {getLocationDisplayName(item.hotspot_name)}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        <span
                          className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] ${getRiskClasses(
                            risk
                          )}`}
                        >
                          {risk}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-right font-mono font-semibold text-cyan-300">
                        {numberFormatter.format(item.total_violations)}
                      </td>
                      <td className="px-4 py-3.5 text-xs text-slate-400">
                        {item.dominant_violation_type}
                      </td>
                      <td className="px-4 py-3.5">
                        <span className="inline-flex items-center gap-1.5 rounded-full border border-white/[0.06] bg-black/20 px-2.5 py-1 text-[10px] text-slate-400">
                          <CarFront className="h-3 w-3" />
                          {item.dominant_vehicle_category}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-center font-mono text-xs text-slate-400">
                        {item.unique_dates}
                      </td>
                      <td className="px-4 py-3.5 text-right font-mono text-[10px] text-slate-500">
                        {item.centroid_lat.toFixed(4)},{" "}
                        {item.centroid_lon.toFixed(4)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        <div className="flex flex-col gap-3 border-t border-white/[0.06] px-5 py-3.5 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-xs text-slate-500">
            Page <span className="font-semibold text-slate-300">{page}</span> of{" "}
            <span className="font-semibold text-slate-300">{totalPages}</span>
            <span className="mx-2 text-slate-700">•</span>
            <span className="font-semibold text-slate-300">
              {numberFormatter.format(total)}
            </span>{" "}
            total hotspots
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={page === 1}
              className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-lg border border-white/[0.08] bg-black/20 text-slate-400 transition hover:border-cyan-300/20 hover:text-white disabled:cursor-not-allowed disabled:opacity-35"
              aria-label="Previous page"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={() =>
                setPage((current) => Math.min(totalPages, current + 1))
              }
              disabled={page === totalPages}
              className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-lg border border-white/[0.08] bg-black/20 text-slate-400 transition hover:border-cyan-300/20 hover:text-white disabled:cursor-not-allowed disabled:opacity-35"
              aria-label="Next page"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
