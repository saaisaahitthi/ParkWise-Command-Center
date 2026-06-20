import { Badge } from "@/components/ui/badge";

export type ForecastRow = {
  id: string;
  hotspot: string;
  currentRisk: "Critical" | "High" | "Medium" | "Low";
  predictedRisk: "Critical" | "High" | "Medium" | "Low";
  change: string;
  confidence: number;
  action: string;
};

const riskVariant: Record<ForecastRow["currentRisk"], "critical" | "high" | "medium" | "low"> = {
  Critical: "critical",
  High: "high",
  Medium: "medium",
  Low: "low",
};

interface ForecastTableProps {
  data: ForecastRow[];
  onSelect: (id: string) => void;
}

export function ForecastTable({ data, onSelect }: ForecastTableProps) {
  return (
    <div className="overflow-hidden rounded-[28px] border border-slate-700 bg-slate-950/80 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <div className="border-b border-slate-800 px-6 py-4">
        <h3 className="text-lg font-semibold text-white">Hotspot forecast table</h3>
        <p className="mt-1 text-sm text-slate-400">Predicted risk and operational guidance for priority zones.</p>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Hotspot</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Current risk</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Predicted risk</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Change %</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Forecast confidence</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Recommended action</th>
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
                  <div className="font-semibold text-white">{row.hotspot}</div>
                </td>
                <td className="px-6 py-4">
                  <Badge variant={riskVariant[row.currentRisk]}>{row.currentRisk}</Badge>
                </td>
                <td className="px-6 py-4 text-slate-100">{row.predictedRisk}</td>
                <td className="px-6 py-4 text-slate-100">{row.change}</td>
                <td className="px-6 py-4 text-slate-100">{row.confidence}%</td>
                <td className="px-6 py-4 text-slate-100">{row.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
