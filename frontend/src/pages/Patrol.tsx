import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { AlertTriangle, Route, CheckCircle, Navigation } from "lucide-react";
import { PageHeader } from "@/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { MapMyIndiaWrapper } from "@/components/maps/MapMyIndiaWrapper";
import { fetchLatestPatrolRoute, generatePatrolRoute } from "@/services/patrol";

function latLngToXY(lat: number, lng: number) {
  const minLat = 23.14;
  const maxLat = 23.18;
  const minLng = 79.92;
  const maxLng = 79.96;

  const x = 20 + ((lng - minLng) / (maxLng - minLng)) * 60;
  const y = 80 - ((lat - minLat) / (maxLat - minLat)) * 60;

  return { x, y };
}

export default function PatrolPage() {
  const [routed, setRouted] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["routing-latest"],
    queryFn: fetchLatestPatrolRoute,
    refetchInterval: 10_000,
  });

  const generateRouteMutation = useMutation({
    mutationFn: generatePatrolRoute,
    onSuccess: () => {
      setRouted(true);
      refetch();
      setTimeout(() => setRouted(false), 3000);
    },
  });

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />
          <p className="text-sm font-semibold">Calculating optimal patrol paths...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto h-12 w-12 mb-3 text-red-500 animate-pulse" />
        <h3 className="text-lg font-semibold text-white">Patrol Stream Disconnected</h3>
        <p className="mt-2 text-sm text-slate-400">
          Verify backend connectivity at{" "}
          <code className="text-red-200">http://127.0.0.1:8000/api/v1</code> or toggle header Mode
          to Mock.
        </p>
      </div>
    );
  }

  const {
    total_stops,
    critical_high_stops,
    total_distance_km,
    estimated_travel_time_minutes,
    route_geometry,
    stop_sequence,
  } = data;

  const points = route_geometry.map((pt) => latLngToXY(pt.lat, pt.lng));

  const polylines = [
    {
      id: "route-poly",
      points,
      route_geometry,
      color: "#60a5fa",
    },
  ];

  const markers = stop_sequence.map((stop) => {
    const { x, y } = latLngToXY(stop.lat, stop.lng);
    const color =
      stop.risk === "Critical" ? "#EF4444" : stop.risk === "High" ? "#F59E0B" : "#3B82F6";

    return {
      id: `stop-${stop.sequence}`,
      lat: stop.lat,
      lng: stop.lng,
      x,
      y,
      label: `${stop.sequence}. ${stop.name}`,
      risk: stop.risk as "Critical" | "High" | "Medium" | "Low",
      color,
    };
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <PageHeader
          title="Patrol Routes"
          description="Optimized patrol itineraries generated dynamically to cover critical hotspots with minimal travel overhead."
        />
        <button
          onClick={() => generateRouteMutation.mutate()}
          disabled={generateRouteMutation.isPending}
          className="flex items-center gap-2 px-5 py-3 rounded-full border border-cyan-800 bg-cyan-950/60 hover:bg-cyan-950 text-cyan-300 font-semibold transition active:scale-95 disabled:opacity-50 cursor-pointer h-fit self-start sm:self-center"
        >
          {generateRouteMutation.isPending ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
          ) : routed ? (
            <CheckCircle size={16} className="text-emerald-400" />
          ) : (
            <Route size={16} />
          )}
          <span>{routed ? "Patrols Recalculated!" : "Recalculate Route Geometry"}</span>
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-4">
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Total Patrol Stops
          </p>
          <p className="mt-4 text-3xl font-bold text-white">{total_stops}</p>
        </Card>
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Critical/High Stops
          </p>
          <p className="mt-4 text-3xl font-bold text-rose-400">{critical_high_stops}</p>
        </Card>
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Total Distance
          </p>
          <p className="mt-4 text-3xl font-bold text-white font-mono">{total_distance_km} km</p>
        </Card>
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Est. Dispatch Duration
          </p>
          <p className="mt-4 text-3xl font-bold text-cyan-300 font-mono">
            {estimated_travel_time_minutes} min
          </p>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.8fr_0.9fr]">
        <MapMyIndiaWrapper
          title="Active Dispatch Pathing Map"
          subtitle="Real-time polyline pathing showing step sequence for the active enforcer shift"
          markers={markers}
          polylines={polylines}
          legendItems={[
            { label: "Dispatch Stop Pin", color: "#60a5fa" },
            { label: "Transit Vector Path", color: "#1e293b" },
          ]}
        />

        <Card className="rounded-[32px] border border-slate-800 bg-slate-950/45 p-6 space-y-4">
          <h3 className="text-md font-semibold text-white mb-2">Stop Dispatch Sequence</h3>
          <div className="relative border-l border-slate-800 ml-4 pl-6 space-y-8">
            {stop_sequence.map((stop) => (
              <div key={stop.sequence} className="relative">
                <span className="absolute -left-[37px] top-0 flex h-6.5 w-6.5 items-center justify-center rounded-full bg-slate-900 border border-slate-700 text-xs font-semibold text-cyan-400 font-mono">
                  {stop.sequence}
                </span>

                <div className="space-y-1">
                  <div className="flex items-center justify-between gap-2">
                    <h4 className="text-sm font-semibold text-slate-200">{stop.name}</h4>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase tracking-wider ${
                        stop.risk === "Critical"
                          ? "border-red-900 bg-red-950/40 text-red-300"
                          : stop.risk === "High"
                            ? "border-amber-900 bg-amber-950/40 text-amber-300"
                            : "border-blue-900 bg-blue-950/40 text-blue-300"
                      }`}
                    >
                      {stop.risk}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 flex items-center gap-1">
                    <Navigation size={10} className="text-slate-600" />
                    Patrol stop rank priority #{stop.sequence}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
