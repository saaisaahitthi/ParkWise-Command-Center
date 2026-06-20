import { Badge } from "@/components/ui/badge";
import { formatNumber } from "@/lib/utils";

export type HotspotRecord = {
  id: string;
  name: string;
  risk: "Critical" | "High" | "Medium" | "Low";
  violations: number;
  peakHour: string;
  officers: number;
  status: "Active" | "Monitoring" | "Stabilized" | "Investigating";
};

const riskBadgeMap: Record<HotspotRecord["risk"], "critical" | "high" | "medium" | "low"> = {
  Critical: "critical",
  High: "high",
  Medium: "medium",
  Low: "low",
};

const statusBadgeMap: Record<HotspotRecord["status"], "critical" | "high" | "medium" | "low"> = {
  Active: "critical",
  Monitoring: "high",
  Stabilized: "low",
  Investigating: "medium",
};

interface HotspotTableProps {
  data: HotspotRecord[];
  onSelect: (id: string) => void;
}

export function HotspotTable({ data, onSelect }: HotspotTableProps) {
  return (
    <div className="overflow-hidden rounded-4xl border border-card-border bg-card-bg shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <div className="border-b border-slate-800 bg-slate-950/80 px-6 py-4">
        <h3 className="text-lg font-semibold text-white">Hotspot table</h3>
        <p className="mt-1 text-sm text-slate-400">Monitor the highest-risk zones and assign patrol assets with confidence.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
          <thead>
            <tr>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Hotspot</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Risk</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Violations</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Peak hour</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Recommended officers</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, index) => (
              <tr
                key={row.id}
                className={`cursor-pointer border-b border-slate-800 transition duration-200 hover:bg-slate-900/70 ${index % 2 === 0 ? "bg-slate-950/80" : "bg-slate-950/60"}`}
                onClick={() => onSelect(row.id)}
              >
                <td className="px-6 py-4">
                  <div className="text-sm font-semibold text-white">{row.name}</div>
                  <div className="text-xs text-slate-500">{row.peakHour}</div>
                </td>
                <td className="px-6 py-4">
                  <Badge variant={riskBadgeMap[row.risk]}>{row.risk}</Badge>
                </td>
                <td className="px-6 py-4 text-slate-100">{formatNumber(row.violations)}</td>
                <td className="px-6 py-4 text-slate-100">{row.peakHour}</td>
                <td className="px-6 py-4 text-slate-100">{row.officers}</td>
                <td className="px-6 py-4">
                  <Badge variant={statusBadgeMap[row.status]}>{row.status}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
