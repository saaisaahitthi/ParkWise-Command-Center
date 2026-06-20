import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  CalendarDays,
  CheckCircle,
  Cpu,
  Gauge,
  ShieldAlert,
  TrendingUp,
} from "lucide-react";
import { PageHeader } from "@/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { apiGet, apiPost } from "@/lib/api";
import { getLocationDisplayName } from "@/data/dashboardPresentationData";

export default function ForecastPage() {
  const [recomputed, setRecomputed] = useState(false);

  // Fetch summary KPIs
  const { data: summary, isLoading: isSummaryLoading, error: summaryError } = useQuery({
    queryKey: ["forecast-summary"],
    queryFn: () => apiGet<any>("/forecast/summary"),
    refetchInterval: 10000,
  });

  // Fetch top predictions
  const { data: topPredictions = [], isLoading: isTopLoading, error: topError } = useQuery({
    queryKey: ["forecast-top"],
    queryFn: () => apiGet<any[]>("/forecast/top"),
    refetchInterval: 10000,
  });

  // Mutation to recompute forecast
  const recomputeMutation = useMutation({
    mutationFn: () => apiPost<any>("/forecast/generate"),
    onSuccess: () => {
      setRecomputed(true);
      setTimeout(() => setRecomputed(false), 3000);
    },
  });

  if (isSummaryLoading || isTopLoading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />
          <p className="text-sm font-semibold">Preparing forecast projections...</p>
        </div>
      </div>
    );
  }

  if (summaryError || topError) {
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto h-12 w-12 mb-3 text-red-500 animate-pulse" />
        <h3 className="text-lg font-semibold text-white">Forecast Stream Disconnected</h3>
        <p className="mt-2 text-sm text-slate-400">
          Verify backend connectivity at <code className="text-red-200">http://127.0.0.1:8000/api/v1</code> or toggle header Mode to Mock.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 pb-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <PageHeader
          eyebrow="Forecasting"
          title="Forecast"
          description="Review predicted violation volumes and future congestion-risk trends."
        />
        <button
          type="button"
          onClick={() => recomputeMutation.mutate()}
          disabled={recomputeMutation.isPending}
          className="flex h-9 w-fit cursor-pointer items-center gap-2 self-start rounded-full border border-cyan-300/20 bg-cyan-300/[0.07] px-3.5 text-xs font-semibold text-cyan-100 shadow-[0_12px_30px_-20px_rgba(34,211,238,0.85)] transition hover:border-cyan-300/30 hover:bg-cyan-300/[0.11] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 sm:self-center"
        >
          {recomputeMutation.isPending ? (
            <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-cyan-300 border-t-transparent" />
          ) : recomputed ? (
            <CheckCircle className="h-3.5 w-3.5 text-emerald-300" />
          ) : (
            <Cpu className="h-3.5 w-3.5" />
          )}
          <span>{recomputed ? "Forecast Updated!" : "Recompute Forecast"}</span>
        </button>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        {[
          {
            label: "Forecast Horizon",
            value: summary?.forecast_horizon ?? "—",
            icon: CalendarDays,
            tone: "text-cyan-200",
          },
          {
            label: "High-Risk Clusters",
            value: summary?.predicted_high_risk_hotspots ?? "—",
            icon: ShieldAlert,
            tone: "text-amber-200",
          },
          {
            label: "Average Forecast Risk Score",
            value: summary?.avg_predicted_eis?.toFixed(1) ?? "—",
            icon: Gauge,
            tone: "text-indigo-200",
          },
        ].map(({ label, value, icon: Icon, tone }) => (
          <Card
            key={label}
            className="relative overflow-hidden rounded-[22px] border-cyan-300/[0.09] bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.08),transparent_38%),linear-gradient(150deg,rgba(14,27,39,0.96),rgba(7,15,24,0.9))] p-4 shadow-[0_22px_60px_-48px_rgba(34,211,238,0.85)]"
          >
            <div className="pointer-events-none absolute -right-10 -top-10 h-24 w-24 rounded-full border border-cyan-300/[0.07]" />
            <div className="relative flex items-center gap-3">
              <span
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-current/15 bg-white/[0.035] ${tone}`}
              >
                <Icon className="h-4 w-4" />
              </span>
              <div className="min-w-0">
                <p className="text-[9px] font-semibold uppercase tracking-[0.17em] text-slate-500">
                  {label}
                </p>
                <p className="mt-1 font-mono text-xl font-bold tracking-tight text-white">
                  {value}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card className="overflow-hidden rounded-[26px] border-cyan-300/[0.08] bg-[linear-gradient(145deg,rgba(14,27,39,0.94),rgba(8,17,27,0.84))] p-0 shadow-[0_28px_80px_-58px_rgba(34,211,238,0.6)]">
        <div className="flex flex-col gap-3 border-b border-white/[0.06] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-[9px] font-semibold uppercase tracking-[0.22em] text-cyan-300/65">
              Forecast intelligence
            </p>
            <h2 className="mt-1 text-base font-semibold text-white">
              Risk Escalation Watchlist
            </h2>
            <p className="mt-0.5 text-[10px] text-slate-500">
              Hotspots with the strongest projected congestion-risk signals
            </p>
          </div>
          <span className="flex w-fit items-center gap-2 rounded-full border border-white/[0.07] bg-black/20 px-3 py-1.5 text-[10px] text-slate-400">
            <TrendingUp className="h-3.5 w-3.5 text-cyan-300" />
            {topPredictions.length} monitored
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="border-b border-white/[0.06] bg-black/15 text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
                <th className="px-5 py-3">Hotspot Location</th>
                <th className="px-4 py-3 text-center">Current Risk Score</th>
                <th className="px-4 py-3 text-center">Forecast Risk Score</th>
                <th className="px-4 py-3 text-center">Predicted Risk</th>
                <th className="px-5 py-3">Suggested Enforcement Focus</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.055] text-sm text-slate-300">
              {topPredictions.map((pred: any) => (
                <tr
                  key={pred.hotspot_id}
                  className="transition duration-200 hover:bg-cyan-300/[0.035]"
                >
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(103,232,249,0.8)]" />
                      <span className="font-semibold text-slate-200">
                        {getLocationDisplayName(pred.name)}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3.5 text-center font-mono text-xs text-slate-400">
                    {pred.current_eis.toFixed(1)}
                  </td>
                  <td className="px-4 py-3.5 text-center">
                    <span className="inline-flex min-w-14 justify-center rounded-lg border border-cyan-300/15 bg-cyan-300/[0.07] px-2 py-1 font-mono text-sm font-bold text-cyan-200">
                      {pred.forecasted_eis.toFixed(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-center">
                    <span
                      className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] ${
                        pred.risk_category === "Critical"
                          ? "border-rose-400/20 bg-rose-400/10 text-rose-200"
                          : pred.risk_category === "High"
                            ? "border-amber-400/20 bg-amber-400/10 text-amber-200"
                            : "border-blue-400/20 bg-blue-400/10 text-blue-200"
                      }`}
                    >
                      {pred.risk_category}
                    </span>
                  </td>
                  <td className="max-w-sm px-5 py-3.5 text-xs leading-5 text-slate-400">
                    {pred.action_recommended}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
