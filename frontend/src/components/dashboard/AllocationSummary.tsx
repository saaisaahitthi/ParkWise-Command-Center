import { Card } from "@/components/ui/card";
import { type AllocationRow } from "./OfficerAllocationTable";

interface Props { rows: AllocationRow[] }

export function AllocationSummary({ rows }: Props) {
  const counts = rows.reduce(
    (acc, r) => {
      acc.total++;
      if (r.risk === "Critical") acc.critical++;
      if (r.risk === "High") acc.high++;
      if (r.risk === "Medium") acc.medium++;
      if (r.risk === "Low") acc.low++;
      acc.recommended += r.recommendedOfficers;
      return acc;
    },
    { total: 0, critical: 0, high: 0, medium: 0, low: 0, recommended: 0 }
  );

  return (
    <Card className="p-5">
      <h3 className="text-sm font-semibold text-white">Allocation summary</h3>
      <p className="mt-1 text-sm text-slate-400">High-level counts and recommended officers.</p>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">Critical hotspots</div>
          <div className="mt-1 text-xl font-semibold text-white">{counts.critical}</div>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">High hotspots</div>
          <div className="mt-1 text-xl font-semibold text-white">{counts.high}</div>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">Medium hotspots</div>
          <div className="mt-1 text-xl font-semibold text-white">{counts.medium}</div>
        </div>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">Low hotspots</div>
          <div className="mt-1 text-xl font-semibold text-white">{counts.low}</div>
        </div>
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
          <div className="text-xs text-slate-400">Recommended officers</div>
          <div className="mt-1 text-xl font-semibold text-white">{counts.recommended}</div>
        </div>
      </div>
    </Card>
  );
}
