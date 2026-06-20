import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

export type AllocationRow = {
  id: string;
  hotspot: string;
  risk: "Critical" | "High" | "Medium" | "Low";
  violations: number;
  recommendedOfficers: number;
  allocatedOfficers: number;
  coverageStatus: "Covered" | "Partially" | "Under-deployed";
  priority: number;
};

const riskVariant: Record<AllocationRow['risk'], "critical" | "high" | "medium" | "low"> = {
  Critical: "critical",
  High: "high",
  Medium: "medium",
  Low: "low",
};

interface Props {
  data: AllocationRow[];
  onSelect?: (id: string) => void;
}

export function OfficerAllocationTable({ data, onSelect }: Props) {
  return (
    <Card className="overflow-hidden rounded-[28px] border border-slate-700 bg-slate-950/80">
      <div className="border-b border-slate-800 px-6 py-4">
        <h3 className="text-lg font-semibold text-white">Officer allocation table</h3>
        <p className="mt-1 text-sm text-slate-400">Recommended vs allocated officers across priority hotspots.</p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Hotspot</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Risk</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Violations</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Recommended</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Allocated</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Coverage</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Priority</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={row.id} className={`cursor-pointer border-b border-slate-800 hover:bg-slate-900/70 ${idx % 2 === 0 ? "bg-slate-950/80" : "bg-slate-950/60"}`} onClick={() => onSelect?.(row.id)}>
                <td className="px-6 py-4"><div className="font-semibold text-white">{row.hotspot}</div></td>
                <td className="px-6 py-4"><Badge variant={riskVariant[row.risk]}>{row.risk}</Badge></td>
                <td className="px-6 py-4 text-slate-100">{row.violations}</td>
                <td className="px-6 py-4 text-slate-100">{row.recommendedOfficers}</td>
                <td className="px-6 py-4 text-slate-100">{row.allocatedOfficers}</td>
                <td className="px-6 py-4 text-slate-100">{row.coverageStatus}</td>
                <td className="px-6 py-4 text-slate-100">#{row.priority}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
