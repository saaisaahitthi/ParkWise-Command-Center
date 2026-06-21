import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
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
import {
  useForecastSummary,
  useTopForecasts,
} from "@/hooks/useForecast";
import { generateForecast, trainForecast } from "@/services/forecast";

type ForecastOperationPhase =
  | "idle"
  | "training"
  | "generating"
  | "success";

function getErrorMessage(error: unknown): string {
  if (error && typeof error === "object" && "message" in error) {
    const message = (error as { message?: unknown }).message;
    if (typeof message === "string" && message.trim()) return message;
  }
  if (error instanceof Error && error.message.trim()) return error.message;
  return "Forecast processing failed. Please try again.";
}

export default function ForecastPage() {
  const [operationPhase, setOperationPhase] =
    useState<ForecastOperationPhase>("idle");
  const [operationError, setOperationError] = useState("");

  const {
    data: summary,
    isLoading: isSummaryLoading,
    error: summaryError,
    refetch: refetchSummary,
  } = useForecastSummary();
  const {
    data: topPredictions = [],
    isLoading: isTopLoading,
    error: topError,
    refetch: refetchTopForecasts,
  } = useTopForecasts();

  const recomputeMutation = useMutation({
    mutationFn: async () => {
      setOperationError("");
      setOperationPhase("training");
      await trainForecast();

      setOperationPhase("generating");
      return generateForecast();
    },
    onSuccess: async () => {
      await Promise.all([refetchSummary(), refetchTopForecasts()]);
      setOperationPhase("success");
      setTimeout(() => setOperationPhase("idle"), 3000);
    },
    onError: (error) => {
      setOperationPhase("idle");
      setOperationError(getErrorMessage(error));
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
    const loadError = getErrorMessage(summaryError ?? topError);
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto h-12 w-12 mb-3 text-red-500 animate-pulse" />
        <h3 className="text-lg font-semibold text-white">Forecast Stream Disconnected</h3>
        <p className="mt-2 text-sm text-slate-400">
          {loadError}
        </p>
      </div>
    );
  }

  const hasForecastData = (summary?.totalForecasts ?? 0) > 0;
  const isProcessing =
    operationPhase === "training" || operationPhase === "generating";
  const buttonLabel =
    operationPhase === "training"
      ? "Training Forecast..."
      : operationPhase === "generating"
        ? "Generating Predictions..."
        : operationPhase === "success"
          ? "Forecast Updated"
          : hasForecastData
            ? "Recompute Forecast"
            : "Generate Forecast";

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
          disabled={isProcessing}
          className="flex h-9 w-fit cursor-pointer items-center gap-2 self-start rounded-full border border-cyan-300/20 bg-cyan-300/[0.07] px-3.5 text-xs font-semibold text-cyan-100 shadow-[0_12px_30px_-20px_rgba(34,211,238,0.85)] transition hover:border-cyan-300/30 hover:bg-cyan-300/[0.11] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 sm:self-center"
        >
          {isProcessing ? (
            <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-cyan-300 border-t-transparent" />
          ) : operationPhase === "success" ? (
            <CheckCircle className="h-3.5 w-3.5 text-emerald-300" />
          ) : (
            <Cpu className="h-3.5 w-3.5" />
          )}
          <span>{buttonLabel}</span>
        </button>
      </div>

      {operationError ? (
        <div className="flex items-start gap-2 rounded-2xl border border-rose-400/20 bg-rose-400/[0.07] px-4 py-3 text-sm text-rose-200">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{operationError}</span>
        </div>
      ) : null}

      {!hasForecastData ? (
        <Card className="rounded-[26px] border-cyan-300/[0.1] bg-[radial-gradient(circle_at_top,rgba(34,211,238,0.09),transparent_42%),linear-gradient(145deg,rgba(14,27,39,0.94),rgba(8,17,27,0.84))] px-6 py-12 text-center shadow-[0_28px_80px_-58px_rgba(34,211,238,0.6)]">
          <span className="mx-auto flex h-11 w-11 items-center justify-center rounded-2xl border border-cyan-300/15 bg-cyan-300/[0.07] text-cyan-200">
            <TrendingUp className="h-5 w-5" />
          </span>
          <h2 className="mt-4 text-lg font-semibold text-white">
            No forecast generated yet
          </h2>
          <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-slate-400">
            Run forecast training to compute predictions.
          </p>
          <button
            type="button"
            onClick={() => recomputeMutation.mutate()}
            disabled={isProcessing}
            className="mt-5 inline-flex h-9 cursor-pointer items-center gap-2 rounded-full border border-cyan-300/20 bg-cyan-300/[0.09] px-4 text-xs font-semibold text-cyan-100 transition hover:border-cyan-300/30 hover:bg-cyan-300/[0.14] disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isProcessing ? (
              <span className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-cyan-300 border-t-transparent" />
            ) : (
              <Cpu className="h-3.5 w-3.5" />
            )}
            {buttonLabel}
          </button>
        </Card>
      ) : (
        <>
      <div className="grid gap-3 sm:grid-cols-3">
        {[
          {
            label: "Forecast Horizon",
            value: summary?.forecastHorizonLabel ?? "—",
            icon: CalendarDays,
            tone: "text-cyan-200",
          },
          {
            label: "High-Risk Clusters",
            value: summary?.predictedHighRiskHotspots ?? "—",
            icon: ShieldAlert,
            tone: "text-amber-200",
          },
          {
            label: "Average Forecast Risk Score",
            value: summary?.avgPredictedEis.toFixed(1) ?? "—",
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
              {topPredictions.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="px-5 py-10 text-center text-sm text-slate-500"
                  >
                    No high-risk forecast signals are present in the current horizon.
                  </td>
                </tr>
              ) : topPredictions.map((pred) => (
                <tr
                  key={pred.hotspot_id}
                  className="transition duration-200 hover:bg-cyan-300/[0.035]"
                >
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(103,232,249,0.8)]" />
                      <span className="min-w-0">
                        <span className="block font-semibold text-slate-200">
                          {pred.displayName}
                        </span>
                        {pred.displaySubtext ? (
                          <span className="mt-0.5 block font-mono text-[9px] text-slate-600">
                            {pred.displaySubtext}
                          </span>
                        ) : null}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3.5 text-center font-mono text-xs text-slate-400">
                    {pred.current_eis?.toFixed(1) ?? "—"}
                  </td>
                  <td className="px-4 py-3.5 text-center">
                    <span className="inline-flex min-w-14 justify-center rounded-lg border border-cyan-300/15 bg-cyan-300/[0.07] px-2 py-1 font-mono text-sm font-bold text-cyan-200">
                      {pred.forecasted_eis.toFixed(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3.5 text-center">
                    <span
                      className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] ${
                        pred.displayRiskTier === "Critical"
                          ? "border-rose-400/20 bg-rose-400/10 text-rose-200"
                          : pred.displayRiskTier === "High"
                            ? "border-amber-400/20 bg-amber-400/10 text-amber-200"
                            : "border-blue-400/20 bg-blue-400/10 text-blue-200"
                      }`}
                    >
                      {pred.displayRiskTier}
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
        </>
      )}
    </div>
  );
}
