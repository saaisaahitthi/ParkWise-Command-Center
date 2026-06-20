import { CoverageChart } from "@/components/charts/CoverageChart";

interface Props {
  metrics: {
    congestion: number;
    responseTime: number;
    coverage: number;
    riskReduction: number;
    utilization: number;
  };
}

export function ImpactMetrics({ metrics }: Props) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-white">Live impact</h4>
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-md border border-slate-700 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">Predicted congestion</div>
          <div className="mt-2 text-2xl font-semibold text-white">{metrics.congestion}</div>
        </div>
        <div className="rounded-md border border-slate-700 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">Response time</div>
          <div className="mt-2 text-2xl font-semibold text-white">{metrics.responseTime} min</div>
        </div>
        <div className="rounded-md border border-slate-700 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">Coverage</div>
          <div className="mt-2"><CoverageChart label="Coverage" value={Math.round(metrics.coverage)} color="#4fd1c5" /></div>
        </div>
        <div className="rounded-md border border-slate-700 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">Risk reduction</div>
          <div className="mt-2 text-2xl font-semibold text-white">{Math.round(metrics.riskReduction)}%</div>
          <div className="text-xs text-slate-400 mt-1">Officer utilization: {Math.round(metrics.utilization)}%</div>
        </div>
      </div>
    </div>
  );
}
