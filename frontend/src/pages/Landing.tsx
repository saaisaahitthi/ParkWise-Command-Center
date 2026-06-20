import { useAppStore } from "@/stores/appStore";
import { ArrowRight, LayoutDashboard, MapPin, TrendingUp, Users, Route, FlaskConical, CircleDot } from "lucide-react";
import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";

export default function LandingPage() {
  const { useMockData, toggleMockData } = useAppStore();

  const navigationCards = [
    { title: "Command Dashboard", path: "/dashboard", desc: "Live KPI overview and city-wide violation heatmaps.", icon: LayoutDashboard, color: "text-sky-400" },
    { title: "Hotspot Intelligence", path: "/hotspots", desc: "Granular risk identification and pin tracking.", icon: MapPin, color: "text-rose-400" },
    { title: "EIS Explainability", path: "/temporal", desc: "Deconstruct why specific intersections are flagged.", icon: TrendingUp, color: "text-amber-400" },
    { title: "Resource Allocation", path: "/officers", desc: "Optimal officer deployment distribution details.", icon: Users, color: "text-teal-400" },
    { title: "Patrol Route Planner", path: "/patrol", desc: "Calculated dispatch route sequencing.", icon: Route, color: "text-purple-400" },
    { title: "What-If Simulator", path: "/simulator", desc: "Test response capacity against virtual congestion.", icon: FlaskConical, color: "text-indigo-400" },
  ];

  return (
    <div className="min-h-[calc(100vh-var(--topbar-height)-var(--statusbar-height))] flex flex-col justify-center text-slate-100 max-w-6xl mx-auto py-8">
      {/* Hero Section */}
      <div className="text-center space-y-6 max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-950/80 px-4 py-2 text-xs uppercase tracking-[0.28em] text-slate-400">
          <CircleDot className="h-3 w-3 text-sky-400 animate-pulse" />
          Parking intelligence • Jabalpur Municipal Corporation
        </div>
        <h1 className="text-4xl md:text-5xl font-semibold tracking-tight text-white font-display">
          Smarter Parking & Congestion Command Center
        </h1>
        <p className="text-slate-300 text-base leading-7 max-w-xl mx-auto">
          Identify parking-induced traffic congestion, predict future risks, allocate field enforcement units, and generate optimized patrol routes.
        </p>
      </div>

      {/* Mode Control Widget */}
      <div className="mb-12 rounded-[28px] border border-slate-800 bg-slate-950/70 p-6 max-w-2xl mx-auto text-center space-y-4 shadow-[0_24px_80px_-50px_rgba(0,0,0,0.8)]">
        <p className="text-xs uppercase tracking-[0.24em] text-slate-400 font-semibold">Integration Telemetry Stream</p>
        <h3 className="text-lg font-semibold text-white">Choose Telemetry Pipeline Source</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Switch the system between running on self-contained simulated datasets (Mock Mode) or connecting to live backend API microservices (Live Mode).
        </p>
        <div className="flex justify-center pt-2">
          <button
            onClick={toggleMockData}
            className={cn(
              "flex items-center gap-3 rounded-full border px-6 py-3 transition-all active:scale-95 cursor-pointer font-semibold",
              useMockData
                ? "border-amber-500/40 bg-amber-500/10 text-amber-300 hover:bg-amber-500/20"
                : "border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20"
            )}
          >
            <span className={cn("h-2.5 w-2.5 rounded-full animate-pulse", useMockData ? "bg-amber-400" : "bg-emerald-400")} />
            <span>Currently Active: {useMockData ? "Mock Simulation Mode" : "Live API Connected"}</span>
          </button>
        </div>
      </div>

      {/* Command Control Links Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {navigationCards.map((card) => {
          const Icon = card.icon;
          return (
            <Link
              key={card.title}
              to={card.path}
              className="group rounded-3xl border border-slate-800 bg-slate-950/45 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-slate-700 hover:bg-slate-950/80 hover:shadow-[0_20px_50px_-30px_rgba(0,212,255,0.15)]"
            >
              <div className="flex items-center justify-between">
                <div className={cn("inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900", card.color)}>
                  <Icon size={24} />
                </div>
                <ArrowRight size={18} className="text-slate-500 group-hover:text-slate-200 transition-colors" />
              </div>
              <h2 className="mt-5 text-lg font-semibold text-white">{card.title}</h2>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">{card.desc}</p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
