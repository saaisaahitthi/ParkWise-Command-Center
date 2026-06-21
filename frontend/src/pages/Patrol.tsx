import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  BrainCircuit,
  CheckCircle,
  Clock3,
  MapPinned,
  Navigation,
  RefreshCw,
  Route,
  Ruler,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { MapMyIndiaWrapper } from "@/components/maps/MapMyIndiaWrapper";
import { PageHeader } from "@/layout/PageHeader";
import {
  fetchLatestPatrolRoute,
  generatePatrolRoute,
} from "@/services/patrol";
import { patrolRouteInsight } from "@/data/patrolPresentationData";

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

export default function PatrolPage() {
  const [routed, setRouted] = useState(false);

  // Fetch latest routing / patrol details
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["routing-latest"],
    queryFn: fetchLatestPatrolRoute,
    refetchInterval: 10000,
  });

  // Recompute route geometry mutation
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
          The current Bengaluru patrol route could not be loaded. Check the
          service connection and try again.
        </p>
      </div>
    );
  }

  const {
    total_stops,
    critical_high_stops,
    total_distance_km,
    estimated_travel_time_minutes,
    route_geometry = [],
    stop_sequence = [],
  } = data;

  // Convert geometry coordinates for visualization
  const points = route_geometry.map((pt) => latLngToXY(pt.lat, pt.lng));

  const polylines = [
    {
      id: "route-poly",
      points,
      route_geometry,
      color: "#60a5fa",
    },
  ];

  // Plot stops as markers
  const markers = stop_sequence.map((stop) => {
    const { x, y } = latLngToXY(stop.lat, stop.lng);
    const color =
      stop.displayRiskTier === "Critical"
        ? "#EF4444"
        : stop.displayRiskTier === "High"
          ? "#F59E0B"
          : stop.displayRiskTier === "Medium"
            ? "#3B82F6"
            : "#10B981";

    return {
      id: `stop-${stop.sequence}`,
      lat: stop.lat,
      lng: stop.lng,
      x,
      y,
      label: `${stop.sequence}. ${stop.displayName}`,
      risk: mapRiskLevel(stop.displayRiskTier),
      color,
    };
  });

  return (
    <div className="relative space-y-4">
      <div className="pointer-events-none absolute -left-16 -top-16 -z-10 h-72 w-72 rounded-full bg-cyan-400/[0.035] blur-3xl" />

      <PageHeader
        eyebrow="Patrol Operations"
        title="Patrol Routes"
        description="Optimized patrol itineraries covering critical hotspots with minimal travel overhead."
        actions={
          <button
            onClick={() => generateRouteMutation.mutate()}
            disabled={generateRouteMutation.isPending}
            className="group flex min-h-10 cursor-pointer items-center gap-2 rounded-xl border border-cyan-300/20 bg-cyan-300/[0.09] px-4 py-2.5 text-xs font-semibold text-cyan-100 shadow-[0_14px_35px_-24px_rgba(34,211,238,0.9)] transition duration-300 hover:-translate-y-0.5 hover:border-cyan-200/30 hover:bg-cyan-300/[0.14] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 sm:text-[13px]"
          >
            {generateRouteMutation.isPending ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
            ) : routed ? (
              <CheckCircle className="h-[18px] w-[18px] text-emerald-300" />
            ) : (
              <RefreshCw className="h-[18px] w-[18px] transition-transform duration-500 group-hover:rotate-90" />
            )}
            <span>
              {routed ? "Patrols Recalculated!" : "Recalculate Route Geometry"}
            </span>
          </button>
        }
      />

      {/* Patrol KPIs */}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <Card className="group relative overflow-hidden rounded-[20px] border-cyan-300/10 bg-[linear-gradient(145deg,rgba(14,28,40,0.94),rgba(8,17,27,0.78))] p-3.5 shadow-[0_22px_55px_-45px_rgba(34,211,238,0.65)] transition duration-300 hover:-translate-y-0.5 hover:border-cyan-300/20">
          <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/50 to-transparent" />
          <div className="flex items-start justify-between gap-4">
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
              Total Patrol Stops
            </p>
            <span className="flex h-8 w-8 items-center justify-center rounded-[10px] border border-cyan-300/10 bg-cyan-300/[0.07] text-cyan-300">
              <MapPinned className="h-4 w-4" />
            </span>
          </div>
          <p className="mt-2 text-3xl font-bold tracking-tight text-white">
            {total_stops}
          </p>
          <p className="mt-0.5 text-[10px] text-slate-500">
            Stops in active sequence
          </p>
        </Card>
        <Card className="group relative overflow-hidden rounded-[20px] border-rose-300/10 bg-[linear-gradient(145deg,rgba(35,20,28,0.9),rgba(15,17,26,0.8))] p-3.5 shadow-[0_22px_55px_-45px_rgba(251,113,133,0.55)] transition duration-300 hover:-translate-y-0.5 hover:border-rose-300/20">
          <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-rose-300/50 to-transparent" />
          <div className="flex items-start justify-between gap-4">
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
              Critical/High Stops
            </p>
            <span className="flex h-8 w-8 items-center justify-center rounded-[10px] border border-rose-300/10 bg-rose-400/[0.07] text-rose-300">
              <ShieldAlert className="h-4 w-4" />
            </span>
          </div>
          <p className="mt-2 text-3xl font-bold tracking-tight text-rose-300">
            {critical_high_stops}
          </p>
          <p className="mt-0.5 text-[10px] text-slate-500">
            Priority interventions
          </p>
        </Card>
        <Card className="group relative overflow-hidden rounded-[20px] border-sky-300/10 bg-[linear-gradient(145deg,rgba(14,25,38,0.92),rgba(8,17,27,0.8))] p-3.5 shadow-[0_22px_55px_-45px_rgba(125,211,252,0.45)] transition duration-300 hover:-translate-y-0.5 hover:border-sky-300/20">
          <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-sky-300/45 to-transparent" />
          <div className="flex items-start justify-between gap-4">
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
              Total Distance
            </p>
            <span className="flex h-8 w-8 items-center justify-center rounded-[10px] border border-sky-300/10 bg-sky-300/[0.06] text-sky-300">
              <Ruler className="h-4 w-4" />
            </span>
          </div>
          <p className="mt-2 font-mono text-2xl font-bold tracking-tight text-white">
            {total_distance_km}
            <span className="ml-2 text-base font-semibold text-slate-500">km</span>
          </p>
          <p className="mt-0.5 text-[10px] text-slate-500">
            Optimized route coverage
          </p>
        </Card>
        <Card className="group relative overflow-hidden rounded-[20px] border-teal-300/10 bg-[linear-gradient(145deg,rgba(11,31,36,0.9),rgba(8,17,27,0.8))] p-3.5 shadow-[0_22px_55px_-45px_rgba(45,212,191,0.5)] transition duration-300 hover:-translate-y-0.5 hover:border-teal-300/20">
          <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-teal-300/50 to-transparent" />
          <div className="flex items-start justify-between gap-4">
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-slate-500">
              Est. Dispatch Duration
            </p>
            <span className="flex h-8 w-8 items-center justify-center rounded-[10px] border border-teal-300/10 bg-teal-300/[0.07] text-teal-300">
              <Clock3 className="h-4 w-4" />
            </span>
          </div>
          <p className="mt-2 font-mono text-2xl font-bold tracking-tight text-cyan-200">
            {estimated_travel_time_minutes}
            <span className="ml-2 text-base font-semibold text-slate-500">min</span>
          </p>
          <p className="mt-0.5 text-[10px] text-slate-500">
            Estimated field travel
          </p>
        </Card>
      </div>

      {/* Main Split Content */}
      <div className="grid items-stretch gap-4 xl:grid-cols-[minmax(0,2.1fr)_minmax(300px,0.9fr)]">
        {/* Route Map */}
        <div className="patrol-map-shell rounded-[30px] border border-cyan-300/10 bg-slate-950/50 p-1.5 shadow-[0_35px_90px_-55px_rgba(34,211,238,0.65)]">
          <MapMyIndiaWrapper
            title="Active Dispatch Pathing Map"
            subtitle="Route geometry visualization with priority-based stop sequencing for the active shift"
            markers={markers}
            polylines={polylines}
            legendItems={[
              { label: "Dispatch Stop Pin", color: "#60a5fa" },
              { label: "Transit Vector Path", color: "#1e293b" },
            ]}
            variant="patrol"
          />
        </div>

        <div className="grid min-h-0 gap-3">
          {/* Timeline Sequence */}
          <Card className="min-h-0 overflow-hidden rounded-[28px] border-white/[0.08] bg-[linear-gradient(155deg,rgba(13,26,38,0.92),rgba(7,15,24,0.82))] p-0 shadow-[0_30px_80px_-52px_rgba(0,0,0,0.9)]">
            <div className="border-b border-white/[0.07] px-4 py-3.5">
              <div className="flex items-center gap-3">
                <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-300/10 bg-cyan-300/[0.07] text-cyan-300">
                  <Route className="h-4 w-4" />
                </span>
                <div>
                  <h3 className="text-base font-semibold text-white">
                    Stop Dispatch Sequence
                  </h3>
                  <p className="mt-0.5 text-xs text-slate-500">
                    Ordered mission path for the active shift
                  </p>
                </div>
              </div>
            </div>

            <div className="max-h-[300px] overflow-y-auto p-3">
              <div className="relative space-y-2 before:absolute before:bottom-5 before:left-[18px] before:top-5 before:w-px before:bg-gradient-to-b before:from-cyan-300/35 before:via-slate-700/50 before:to-transparent">
                {stop_sequence.map((stop) => (
                  <div
                    key={stop.sequence}
                    className="group relative grid grid-cols-[38px_1fr] gap-2.5 rounded-2xl border border-transparent p-2 transition duration-300 hover:-translate-y-0.5 hover:border-white/[0.07] hover:bg-white/[0.035]"
                  >
                    <span className="relative z-10 flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-300/15 bg-[#0b1823] font-mono text-[11px] font-bold text-cyan-300 shadow-[0_0_20px_-10px_rgba(103,232,249,0.8)]">
                      {String(stop.sequence).padStart(2, "0")}
                    </span>

                    <div className="min-w-0 rounded-xl border border-white/[0.055] bg-black/10 px-3 py-2.5 transition group-hover:border-white/[0.09] group-hover:bg-white/[0.025]">
                      <div className="flex items-start justify-between gap-3">
                        <h4 className="min-w-0 truncate text-sm font-semibold text-slate-100">
                          {stop.displayName}
                        </h4>
                        <span
                          className={`shrink-0 rounded-full border px-2.5 py-1 text-[9px] font-bold uppercase tracking-[0.12em] shadow-sm ${
                            stop.displayRiskTier === "Critical"
                              ? "border-rose-400/20 bg-rose-400/[0.1] text-rose-200 shadow-rose-500/10"
                              : stop.displayRiskTier === "High"
                                ? "border-amber-300/20 bg-amber-300/[0.09] text-amber-200 shadow-amber-500/10"
                                : "border-sky-300/20 bg-sky-300/[0.08] text-sky-200 shadow-sky-500/10"
                          }`}
                        >
                          {stop.displayRiskTier}
                        </span>
                      </div>
                      <p className="mt-1.5 flex items-center gap-1.5 text-[11px] text-slate-500">
                        <Navigation className="h-3 w-3 text-slate-600" />
                        {stop.displaySubtext}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card className="relative overflow-hidden rounded-[22px] border-cyan-300/10 bg-[linear-gradient(145deg,rgba(11,30,38,0.9),rgba(7,16,25,0.82))] p-4 shadow-[0_24px_60px_-45px_rgba(34,211,238,0.6)]">
            <span className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/45 to-transparent" />
            <div className="flex items-start gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-cyan-300/12 bg-cyan-300/[0.07] text-cyan-300">
                <BrainCircuit className="h-4 w-4" />
              </span>
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-semibold text-white">
                    {patrolRouteInsight.title}
                  </h3>
                  <Sparkles className="h-3 w-3 text-cyan-300/70" />
                </div>
                <p className="mt-1.5 text-[11px] leading-5 text-slate-400">
                  {patrolRouteInsight.description}
                </p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {patrolRouteInsight.highlights.map((highlight) => (
                    <span
                      key={highlight}
                      className="rounded-full border border-white/[0.07] bg-white/[0.035] px-2.5 py-1 text-[9px] font-medium text-slate-300"
                    >
                      {highlight}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
