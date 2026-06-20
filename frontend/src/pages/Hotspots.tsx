import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, ChevronLeft, ChevronRight, Search } from "lucide-react";
import { PageHeader } from "@/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { MapMyIndiaWrapper } from "@/components/maps/MapMyIndiaWrapper";
import { apiGet } from "@/lib/api";

function latLngToXY(lat: number, lng: number) {
  const minLat = 23.14;
  const maxLat = 23.18;
  const minLng = 79.92;
  const maxLng = 79.96;

  const x = 20 + ((lng - minLng) / (maxLng - minLng)) * 60;
  const y = 80 - ((lat - minLat) / (maxLat - minLat)) * 60;

  return { x, y };
}

export default function HotspotsPage() {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [minViolations, setMinViolations] = useState(0);
  const [selectedHotspotName, setSelectedHotspotName] = useState<string>("");

  const { data, isLoading, error } = useQuery({
    queryKey: ["hotspots", page, minViolations],
    queryFn: () =>
      apiGet<any>(
        `/hotspots?page=${page}&page_size=10&min_violations=${minViolations}`
      ),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />
          <p className="text-sm font-semibold">Loading hotspots database...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto h-12 w-12 mb-3 text-red-500 animate-pulse" />
        <h3 className="text-lg font-semibold text-white">Hotspots Stream Disconnected</h3>
        <p className="mt-2 text-sm text-slate-400">
          Verify backend connectivity at <code className="text-red-200">http://127.0.0.1:8000/api/v1</code> or toggle header Mode to Mock.
        </p>
      </div>
    );
  }

  const { items = [], total = 0, page_size = 10 } = data;

  // Filter items based on local search query for fluid visual filtering
  const filteredItems = items.filter((item: any) =>
    item.hotspot_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Compute map pins
  const markers = filteredItems.map((item: any) => {
    const { x, y } = latLngToXY(item.centroid_lat, item.centroid_lon);
    // Categorize risk based on violations for visual indicators
    const isCritical = item.total_violations >= 650;
    const isHigh = item.total_violations >= 450 && item.total_violations < 650;
    const risk = isCritical ? "Critical" : isHigh ? "High" : "Medium";
    const color = isCritical ? "#EF4444" : isHigh ? "#F59E0B" : "#3B82F6";

    return {
      id: item.hotspot_name,
      lat: item.centroid_lat,
      lng: item.centroid_lon,
      x,
      y,
      label: item.hotspot_name,
      risk,
      color,
      selected: item.hotspot_name === selectedHotspotName,
    };
  });

  const selectedHotspot = filteredItems.find(
    (h: any) => h.hotspot_name === selectedHotspotName
  );
  const popups = selectedHotspot
    ? [
        {
          id: `popup-${selectedHotspot.hotspot_name}`,
          title: selectedHotspot.hotspot_name,
          description: `Total Violations: ${selectedHotspot.total_violations} | Dominant: ${selectedHotspot.dominant_violation_type} (${selectedHotspot.dominant_vehicle_category})`,
          position: latLngToXY(
            selectedHotspot.centroid_lat,
            selectedHotspot.centroid_lon
          ),
          latLng: [selectedHotspot.centroid_lat, selectedHotspot.centroid_lon] as [number, number],
          open: true,
        },
      ]
    : [];

  const totalPages = Math.max(1, Math.ceil(total / page_size));

  return (
    <div className="space-y-6">
      <PageHeader
        title="Hotspot Intelligence"
        description="Bengaluru parking violation density, priority zones, and hotspot records."
      />

      <div className="grid gap-6 xl:grid-cols-[280px_1fr]">
        {/* Filters Sidebar */}
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/60 p-5 space-y-6 h-fit">
          <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">
            Filters
          </h3>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400">Search Area</label>
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search hotspot..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-2xl border border-slate-700 bg-slate-950/80 py-2.5 pl-9 pr-4 text-sm text-white placeholder-slate-500 focus:border-cyan-500 outline-none"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-400">
              Min Violations: {minViolations}
            </label>
            <input
              type="range"
              min="0"
              max="800"
              step="50"
              value={minViolations}
              onChange={(e) => {
                setMinViolations(Number(e.target.value));
                setPage(1);
              }}
              className="w-full accent-cyan-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
            />
          </div>
        </Card>

        {/* Map View */}
        <MapMyIndiaWrapper
          title="Spatial Hotspot Cluster Distribution"
          subtitle="Click pins or table records to inspect individual congestion centroids"
          markers={markers}
          popups={popups}
          legendItems={[
            { label: "Critical (>=650)", color: "#EF4444" },
            { label: "High (450-649)", color: "#F59E0B" },
            { label: "Medium (<450)", color: "#3B82F6" },
          ]}
          onMarkerClick={(marker) => setSelectedHotspotName(marker.id)}
        />
      </div>

      {/* Simplified Hotspots Table */}
      <Card className="rounded-[32px] border border-slate-800 bg-slate-950/45 p-6 overflow-hidden">
        <h3 className="text-md font-semibold text-white mb-4">Hotspot Analysis Database</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-xs font-semibold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-4">Hotspot Name</th>
                <th className="py-3 px-4 text-right">Total Violations</th>
                <th className="py-3 px-4">Dominant Violation</th>
                <th className="py-3 px-4">Dominant Vehicle</th>
                <th className="py-3 px-4 text-center">Unique Days</th>
                <th className="py-3 px-4 text-right">Centroid Latitude</th>
                <th className="py-3 px-4 text-right">Centroid Longitude</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-sm text-slate-300">
              {filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-500">
                    No hotspots match the filter parameters.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item: any) => (
                  <tr
                    key={item.hotspot_name}
                    onClick={() => setSelectedHotspotName(item.hotspot_name)}
                    className={`cursor-pointer transition-colors hover:bg-slate-900/35 ${
                      item.hotspot_name === selectedHotspotName
                        ? "bg-slate-900/65 text-white"
                        : ""
                    }`}
                  >
                    <td className="py-3.5 px-4 font-medium text-slate-200">
                      {item.hotspot_name}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-cyan-300 font-semibold">
                      {item.total_violations}
                    </td>
                    <td className="py-3.5 px-4">{item.dominant_violation_type}</td>
                    <td className="py-3.5 px-4">
                      <span className="bg-slate-900 px-2.5 py-1 rounded-full text-xs text-slate-400">
                        {item.dominant_vehicle_category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono">{item.unique_dates}</td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      {item.centroid_lat.toFixed(5)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      {item.centroid_lon.toFixed(5)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-slate-800">
          <p className="text-xs text-slate-500">
            Showing Page <span className="font-semibold text-slate-300">{page}</span> of{" "}
            <span className="font-semibold text-slate-300">{totalPages}</span> (
            <span className="font-semibold text-slate-300">{total}</span> total zones)
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="flex items-center justify-center h-9 w-9 rounded-xl border border-slate-800 bg-slate-950 text-slate-400 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="flex items-center justify-center h-9 w-9 rounded-xl border border-slate-800 bg-slate-950 text-slate-400 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
