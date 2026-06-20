import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { AlertTriangle, Cpu, CheckCircle } from "lucide-react";
import { PageHeader } from "@/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { useForecastSummary, useTopForecasts } from "@/hooks/useForecast";
import { generateForecasts } from "@/services/forecast";

export default function ForecastPage() {
  const [recomputed, setRecomputed] = useState(false);

  const { data: summary, isLoading: isSummaryLoading, error: summaryError } =
    useForecastSummary();
  const {
    data: topPredictions = [],
    isLoading: isTopLoading,
    error: topError,
  } = useTopForecasts();

  const recomputeMutation = useMutation({
    mutationFn: generateForecasts,
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
          <p className="text-sm font-semibold">Running AI prediction engine...</p>
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
          Verify backend connectivity at{" "}
          <code className="text-red-200">http://127.0.0.1:8000/api/v1</code> or toggle header Mode
          to Mock.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <PageHeader
          title="AI Forecasting"
          description="Predict traffic violation volumes and congestion risk trends using deep learning telemetry."
        />
        <button
          onClick={() => recomputeMutation.mutate()}
          disabled={recomputeMutation.isPending}
          className="flex items-center gap-2 px-5 py-3 rounded-full border border-cyan-800 bg-cyan-950/60 hover:bg-cyan-950 text-cyan-300 font-semibold transition active:scale-95 disabled:opacity-50 cursor-pointer h-fit self-start sm:self-center"
        >
          {recomputeMutation.isPending ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
          ) : recomputed ? (
            <CheckCircle size={16} className="text-emerald-400" />
          ) : (
            <Cpu size={16} />
          )}
          <span>{recomputed ? "Forecast Updated!" : "Recompute AI Forecast"}</span>
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Forecast Horizon
          </p>
          <p className="mt-4 text-3xl font-bold text-white">
            {summary?.forecastHorizonLabel ?? "—"}
          </p>
        </Card>
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            High-Risk Clusters
          </p>
          <p className="mt-4 text-3xl font-bold text-white">
            {summary?.predictedHighRiskHotspots ?? 0}
          </p>
        </Card>
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Average Forecasted EIS
          </p>
          <p className="mt-4 text-3xl font-bold text-white font-mono">
            {summary?.avgPredictedEis.toFixed(1) ?? "—"}
          </p>
        </Card>
      </div>

      <Card className="rounded-[32px] border border-slate-800 bg-slate-950/45 p-6 overflow-hidden">
        <h3 className="text-md font-semibold text-white mb-4 font-display">
          Predicted Risk Escalation Nodes
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-xs font-semibold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-4">Hotspot Location</th>
                <th className="py-3 px-4 text-center">Current EIS</th>
                <th className="py-3 px-4 text-center">Forecasted EIS</th>
                <th className="py-3 px-4 text-center">Predicted Risk</th>
                <th className="py-3 px-4">AI Recommended Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-sm text-slate-300">
              {topPredictions.map((pred) => (
                <tr key={pred.hotspot_id} className="hover:bg-slate-900/25 transition-colors">
                  <td className="py-4 px-4 font-medium text-slate-200">{pred.name}</td>
                  <td className="py-4 px-4 text-center font-mono text-slate-400">
                    {pred.current_eis != null ? pred.current_eis.toFixed(1) : "—"}
                  </td>
                  <td className="py-4 px-4 text-center font-mono text-cyan-300 font-bold">
                    {pred.forecasted_eis.toFixed(1)}
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span
                      className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                        pred.risk_category === "Critical"
                          ? "border-red-900 bg-red-950/40 text-red-300"
                          : pred.risk_category === "High"
                            ? "border-amber-900 bg-amber-950/40 text-amber-300"
                            : "border-blue-900 bg-blue-950/40 text-blue-300"
                      }`}
                    >
                      {pred.risk_category}
                    </span>
                  </td>
                  <td className="py-4 px-4 text-xs text-slate-400 italic">
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
