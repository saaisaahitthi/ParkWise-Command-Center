import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
  ShieldCheck,
  Sparkles,
  Target,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { apiGet } from "@/lib/api";
import { PageHeader } from "@/layout/PageHeader";

interface RiskScoreRecord {
  hotspot_id: string;
  rank: number;
  eis_score: number;
  risk_category: string;
  frequency_score: number;
  recurrence_score: number;
  density_score: number;
  temporal_risk_score: number;
  severity_norm: number;
  exposure_score: number;
  severity_multiplier: number;
}

function formatHotspotId(hotspotId: string) {
  return String(hotspotId)
    .replace("hotspot-", "")
    .toUpperCase()
    .split("-")
    .join(" ");
}

function riskClasses(risk: string) {
  if (risk === "Critical") {
    return "border-rose-400/20 bg-rose-400/10 text-rose-200";
  }
  if (risk === "High") {
    return "border-amber-400/20 bg-amber-400/10 text-amber-200";
  }
  if (risk === "Low") {
    return "border-emerald-400/20 bg-emerald-400/10 text-emerald-200";
  }
  return "border-blue-400/20 bg-blue-400/10 text-blue-200";
}

function ScoreBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const width = Math.min(100, Math.max(0, value * 100));

  return (
    <div>
      <div className="mb-1.5 flex justify-between gap-3 text-[11px] font-semibold text-slate-400">
        <span>{label}</span>
        <span className="font-mono text-slate-200">{value.toFixed(2)}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-slate-800/90">
        <div
          className={`h-full rounded-full ${color}`}
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

export default function TemporalPage() {
  const [selectedHotspotId, setSelectedHotspotId] = useState("");

  const { data = [], isLoading, error } = useQuery({
    queryKey: ["eis-scores"],
    queryFn: () => apiGet<RiskScoreRecord[]>("/eis/scores"),
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />
          <p className="text-sm font-semibold">Calculating risk breakdowns…</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto mb-3 h-12 w-12 text-red-500" />
        <h3 className="text-lg font-semibold text-white">
          Risk score data is unavailable
        </h3>
        <p className="mt-2 text-sm text-slate-400">
          The current score breakdown could not be loaded. Please check the
          service connection and try again.
        </p>
      </div>
    );
  }

  const selectedScore =
    data.find((item) => item.hotspot_id === selectedHotspotId) ?? data[0];

  return (
    <div className="space-y-4 pb-6">
      <PageHeader
        eyebrow="Risk Intelligence"
        title="Risk Score Breakdown"
        description="Understand how each hotspot's risk score is calculated."
      />

      <div className="grid items-start gap-4 xl:grid-cols-[minmax(0,1fr)_340px]">
        <Card className="relative isolate min-h-[500px] overflow-hidden rounded-[26px] border-cyan-300/[0.09] bg-[radial-gradient(circle_at_82%_78%,rgba(34,211,238,0.08),transparent_32%),linear-gradient(145deg,rgba(14,27,39,0.96),rgba(7,15,24,0.9))] p-0 shadow-[0_30px_85px_-62px_rgba(34,211,238,0.75)]">
          <div
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 -z-10 opacity-35 [background-image:linear-gradient(rgba(103,232,249,0.055)_1px,transparent_1px),linear-gradient(90deg,rgba(103,232,249,0.055)_1px,transparent_1px)] [background-size:34px_34px] [mask-image:linear-gradient(to_bottom,transparent_20%,black_72%,transparent_100%)]"
          />
          <svg
            aria-hidden="true"
            className="pointer-events-none absolute inset-x-0 bottom-0 -z-10 h-40 w-full opacity-30"
            viewBox="0 0 900 180"
            preserveAspectRatio="none"
          >
            <path
              d="M-40 150 C120 58 218 166 350 96 S560 32 690 106 S824 150 950 52"
              fill="none"
              stroke="rgba(103,232,249,0.32)"
              strokeWidth="2"
              strokeDasharray="8 12"
            />
            <path
              d="M80 190 C204 92 330 144 458 72 S682 110 850 18"
              fill="none"
              stroke="rgba(148,163,184,0.16)"
              strokeWidth="12"
            />
            <circle cx="350" cy="96" r="5" fill="rgba(103,232,249,0.6)" />
            <circle cx="690" cy="106" r="4" fill="rgba(251,191,36,0.55)" />
          </svg>

          <div className="relative z-10 flex items-center justify-between gap-4 border-b border-white/[0.06] bg-[#0b1722]/75 px-5 py-4 backdrop-blur-sm">
            <div>
              <p className="text-[9px] font-semibold uppercase tracking-[0.22em] text-cyan-300/65">
                Priority order
              </p>
              <h2 className="mt-1 text-base font-semibold text-white">
                Hotspot Risk Rankings
              </h2>
              <p className="mt-0.5 text-[10px] text-slate-500">
                Select a record to inspect its score components
              </p>
            </div>
            <span className="hidden items-center gap-2 rounded-full border border-white/[0.07] bg-black/20 px-3 py-1.5 text-[10px] text-slate-400 sm:flex">
              <Target className="h-3.5 w-3.5 text-cyan-300" />
              {data.length} ranked hotspots
            </span>
          </div>

          <div className="relative z-10 overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="border-b border-white/[0.06] bg-black/20 text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
                  <th className="px-4 py-3 text-center">Rank</th>
                  <th className="px-4 py-3">Hotspot</th>
                  <th className="px-4 py-3 text-right">Risk score</th>
                  <th className="px-4 py-3 text-center">Risk tier</th>
                  <th className="px-4 py-3 text-right">Frequency</th>
                  <th className="px-4 py-3 text-right">Recurrence</th>
                  <th className="px-4 py-3 text-right">Density</th>
                  <th className="px-4 py-3 text-right">Temporal risk</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.055] text-sm text-slate-300">
                {data.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-4 py-10 text-center text-slate-500">
                      No risk score records are currently available.
                    </td>
                  </tr>
                ) : (
                  data.map((item) => {
                    const isSelected =
                      item.hotspot_id === selectedScore?.hotspot_id;

                    return (
                      <tr
                        key={item.hotspot_id}
                        onClick={() => setSelectedHotspotId(item.hotspot_id)}
                        className={`cursor-pointer transition duration-200 hover:bg-cyan-300/[0.04] ${
                          isSelected
                            ? "bg-cyan-300/[0.075] text-white shadow-[inset_3px_0_0_rgba(103,232,249,0.82)]"
                            : ""
                        }`}
                      >
                        <td className="px-4 py-3.5 text-center tabular-nums">
                          <span
                            className={`inline-flex h-7 min-w-8 items-center justify-center rounded-full border px-2 font-mono text-[10px] font-bold shadow-inner ${
                              isSelected
                                ? "border-cyan-300/30 bg-cyan-300/[0.12] text-cyan-100 shadow-cyan-300/10"
                                : "border-white/[0.08] bg-black/20 text-slate-500 shadow-black/20"
                            }`}
                          >
                            #{item.rank}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 font-medium text-slate-200">
                          {formatHotspotId(item.hotspot_id)}
                        </td>
                        <td className="px-4 py-3.5 text-right font-mono font-bold tabular-nums text-cyan-200">
                          {item.eis_score.toFixed(1)}
                        </td>
                        <td className="px-4 py-3.5 text-center">
                          <span
                            className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] shadow-[0_8px_20px_-14px_currentColor] ${riskClasses(
                              item.risk_category
                            )}`}
                          >
                            {item.risk_category}
                          </span>
                        </td>
                        <td className="px-4 py-3.5 text-right font-mono text-xs tabular-nums text-slate-400">
                          {item.frequency_score.toFixed(2)}
                        </td>
                        <td className="px-4 py-3.5 text-right font-mono text-xs tabular-nums text-slate-400">
                          {item.recurrence_score.toFixed(2)}
                        </td>
                        <td className="px-4 py-3.5 text-right font-mono text-xs tabular-nums text-slate-400">
                          {item.density_score.toFixed(2)}
                        </td>
                        <td className="px-4 py-3.5 text-right font-mono text-xs tabular-nums text-slate-400">
                          {item.temporal_risk_score.toFixed(2)}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {selectedScore && (
          <Card className="relative h-fit overflow-hidden rounded-[26px] border-cyan-300/[0.14] bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.12),transparent_36%),linear-gradient(150deg,rgba(13,26,38,0.98),rgba(7,15,24,0.95))] shadow-[0_28px_75px_-52px_rgba(34,211,238,0.9)]">
            <div className="pointer-events-none absolute -right-16 -top-16 h-36 w-36 rounded-full border border-cyan-300/[0.08]" />
            <div className="relative border-b border-white/[0.07] p-5">
              <p className="text-[9px] font-semibold uppercase tracking-[0.22em] text-cyan-300/65">
                Selected Hotspot Breakdown
              </p>
              <div className="mt-2 flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-display text-xl font-bold tracking-tight text-white">
                    {formatHotspotId(selectedScore.hotspot_id)}
                  </h2>
                  <p className="mt-1 text-[10px] text-slate-500">
                    Rank #{selectedScore.rank} in current priority order
                  </p>
                </div>
                <span
                  className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] shadow-[0_8px_20px_-14px_currentColor] ${riskClasses(
                    selectedScore.risk_category
                  )}`}
                >
                  {selectedScore.risk_category}
                </span>
              </div>
            </div>

            <div className="relative space-y-5 p-5">
              <ScoreBar
                label="Frequency Weight"
                value={selectedScore.frequency_score}
                color="bg-teal-400"
              />
              <ScoreBar
                label="Recurrence Index"
                value={selectedScore.recurrence_score}
                color="bg-cyan-400"
              />
              <ScoreBar
                label="Spatial Density"
                value={selectedScore.density_score}
                color="bg-indigo-400"
              />
              <ScoreBar
                label="Temporal Volatility"
                value={selectedScore.temporal_risk_score}
                color="bg-amber-400"
              />
            </div>

            <div className="relative border-t border-white/[0.07] bg-black/20 p-5">
              <div className="space-y-3">
                {[
                  ["Severity", selectedScore.severity_norm.toFixed(2)],
                  ["Exposure", selectedScore.exposure_score.toFixed(2)],
                  [
                    "Severity Multiplier",
                    `×${selectedScore.severity_multiplier.toFixed(2)}`,
                  ],
                ].map(([label, value]) => (
                  <div
                    key={label}
                    className="flex items-center justify-between gap-4 text-xs"
                  >
                    <span className="text-slate-500">{label}</span>
                    <span className="font-mono font-semibold text-slate-200">
                      {value}
                    </span>
                  </div>
                ))}
              </div>

              <div className="mt-4 flex items-end justify-between gap-4 rounded-2xl border border-cyan-300/20 bg-[linear-gradient(135deg,rgba(34,211,238,0.1),rgba(34,211,238,0.035))] p-4 shadow-[0_16px_36px_-28px_rgba(34,211,238,0.95)]">
                <div>
                  <p className="text-[9px] font-semibold uppercase tracking-[0.16em] text-cyan-300/65">
                    Final Risk Score
                  </p>
                  <p className="mt-1 text-[10px] text-slate-500">
                    Composite priority value
                  </p>
                </div>
                <span className="font-mono text-[28px] font-bold tracking-tight tabular-nums text-cyan-100 drop-shadow-[0_0_16px_rgba(103,232,249,0.28)]">
                  {selectedScore.eis_score.toFixed(1)}
                </span>
              </div>
            </div>
          </Card>
        )}
      </div>

      <section className="relative overflow-hidden rounded-[28px] border border-cyan-300/[0.11] bg-[radial-gradient(circle_at_15%_0%,rgba(34,211,238,0.12),transparent_30%),linear-gradient(145deg,rgba(11,25,37,0.98),rgba(6,14,23,0.96))] p-5 shadow-[0_30px_85px_-60px_rgba(34,211,238,0.75)] sm:p-6">
        <div className="pointer-events-none absolute -right-20 -top-28 h-72 w-72 rounded-full border border-cyan-300/[0.07]" />
        <div className="relative">
          <div className="flex items-start gap-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-cyan-300/15 bg-cyan-300/[0.07] text-cyan-200">
              <Sparkles className="h-[18px] w-[18px]" />
            </span>
            <div>
              <p className="text-[9px] font-semibold uppercase tracking-[0.24em] text-cyan-300/65">
                Calculation guide
              </p>
              <h2 className="mt-1 font-display text-xl font-bold tracking-tight text-white">
                How Risk Score is Calculated
              </h2>
            </div>
          </div>

          <div className="mt-5 rounded-2xl border border-white/[0.08] bg-black/20 px-4 py-5 text-center sm:px-6">
            <p className="font-mono text-sm font-semibold leading-7 text-slate-200 sm:text-base">
              <span className="text-cyan-200">Risk Score</span>
              {" = "}
              <span className="text-white">
                (Frequency + Recurrence + Density + Temporal Risk)
              </span>
              <span className="mx-2 text-slate-600">×</span>
              <span className="text-amber-200">Severity Multiplier</span>
            </p>
          </div>

          <div className="mt-4 flex items-center gap-2 rounded-xl border border-white/[0.06] bg-white/[0.025] px-4 py-3 text-xs text-slate-400">
            <ShieldCheck className="h-3.5 w-3.5 shrink-0 text-cyan-300" />
            <span>
              This score helps prioritize enforcement attention and deployment
              planning.
            </span>
          </div>
        </div>
      </section>
    </div>
  );
}
