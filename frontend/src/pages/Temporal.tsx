import { useState } from "react";
import { AlertTriangle, Info } from "lucide-react";
import { PageHeader } from "@/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { useEisScores } from "@/hooks/useTemporal";

export default function TemporalPage() {
  const [selectedHotspotId, setSelectedHotspotId] = useState<number | null>(null);

  const { data = [], isLoading, error } = useEisScores();

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />
          <p className="text-sm font-semibold">Deconstructing EIS algorithms...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto h-12 w-12 mb-3 text-red-500 animate-pulse" />
        <h3 className="text-lg font-semibold text-white">EIS Stream Disconnected</h3>
        <p className="mt-2 text-sm text-slate-400">
          Verify backend connectivity at{" "}
          <code className="text-red-200">http://127.0.0.1:8000/api/v1</code> or toggle header Mode
          to Mock.
        </p>
      </div>
    );
  }

  const selectedScore =
    data.find((item) => item.hotspot_id === selectedHotspotId) ?? data[0] ?? null;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Risk Intelligence & EIS Explainability"
        description="Verify how the Enforcer Intensity Score (EIS) is calculated for each congestion node."
      />

      <div className="grid gap-6 xl:grid-cols-[1fr_350px]">
        <Card className="rounded-[32px] border border-slate-800 bg-slate-950/45 p-6 overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-md font-semibold text-white">Hotspot EIS Rankings</h3>
            <span className="text-xs text-slate-400 bg-slate-900 px-3 py-1.5 rounded-full flex items-center gap-1.5">
              <Info size={13} className="text-cyan-400" />
              Formula: EIS = (Freq + Recur + Dens + Temp) * Severity Multiplier
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4 text-center">Rank</th>
                  <th className="py-3 px-4">Hotspot ID</th>
                  <th className="py-3 px-4 text-right">EIS Score</th>
                  <th className="py-3 px-4 text-center">Risk Tier</th>
                  <th className="py-3 px-4 text-right">Frequency</th>
                  <th className="py-3 px-4 text-right">Recurrence</th>
                  <th className="py-3 px-4 text-right">Density</th>
                  <th className="py-3 px-4 text-right">Temporal</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-sm text-slate-300">
                {data.map((item) => (
                  <tr
                    key={item.hotspot_id}
                    onClick={() => setSelectedHotspotId(item.hotspot_id)}
                    className={`cursor-pointer transition-colors hover:bg-slate-900/35 ${
                      item.hotspot_id === selectedScore?.hotspot_id
                        ? "bg-slate-900/60 text-white"
                        : ""
                    }`}
                  >
                    <td className="py-3.5 px-4 text-center font-mono font-bold text-slate-400">
                      #{item.rank ?? "—"}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-200">
                      {item.hotspot_label}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-cyan-300 font-semibold">
                      {item.eis_score.toFixed(1)}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                          item.risk_category === "Critical"
                            ? "border-red-900 bg-red-950/40 text-red-300"
                            : item.risk_category === "High"
                              ? "border-amber-900 bg-amber-950/40 text-amber-300"
                              : "border-blue-900 bg-blue-950/40 text-blue-300"
                        }`}
                      >
                        {item.risk_category}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      {item.frequency_score.toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      {item.recurrence_score.toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      {item.density_score.toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      {item.temporal_risk_score.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {selectedScore && (
          <Card className="rounded-[32px] border border-slate-800 bg-slate-950/70 p-6 space-y-6 h-fit shadow-[0_20px_50px_-30px_rgba(0,0,0,0.8)] border-cyan-900/30">
            <div>
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                Selected Node Explainability
              </p>
              <h3 className="text-xl font-bold text-white mt-1">{selectedScore.hotspot_label}</h3>
            </div>

            <div className="space-y-4">
              {(
                [
                  ["Frequency Weight", selectedScore.frequency_score, "bg-teal-400"],
                  ["Recurrence Index", selectedScore.recurrence_score, "bg-cyan-400"],
                  ["Spatial Density", selectedScore.density_score, "bg-indigo-400"],
                  ["Temporal Volatility", selectedScore.temporal_risk_score, "bg-amber-400"],
                ] as const
              ).map(([label, value, colorClass]) => (
                <div key={label}>
                  <div className="flex justify-between text-xs font-semibold text-slate-400 mb-1">
                    <span>{label}</span>
                    <span className="font-mono text-slate-200">{value.toFixed(2)}</span>
                  </div>
                  <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${colorClass}`}
                      style={{ width: `${value * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-slate-800/80 space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Severity Norm:</span>
                <span className="font-mono text-slate-200 font-semibold">
                  {selectedScore.severity_norm.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Exposure Score:</span>
                <span className="font-mono text-slate-200 font-semibold">
                  {selectedScore.exposure_score.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Severity Multiplier:</span>
                <span className="font-mono text-rose-300 font-bold">
                  x{selectedScore.severity_multiplier.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center text-md font-semibold pt-2 border-t border-slate-800/60">
                <span className="text-white">Final Score:</span>
                <span className="font-mono text-lg text-cyan-300 font-bold">
                  {selectedScore.eis_score.toFixed(1)}
                </span>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
