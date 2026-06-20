import { Card } from "@/components/ui/card";

export type RouteRow = {
  id: string;
  team: string;
  hotspotsCovered: string[];
  distanceKm: number;
  eta: string;
  priority: "High" | "Medium" | "Low";
  status: string;
  stops: number;
  efficiency: number;
};

interface Props { data: RouteRow[]; onSelect?: (id: string) => void }

export function RouteTable({ data, onSelect }: Props) {
  return (
    <Card className="overflow-hidden rounded-[28px] border border-slate-700 bg-slate-950/80">
      <div className="border-b border-slate-800 px-6 py-4">
        <h3 className="text-lg font-semibold text-white">Patrol routes</h3>
        <p className="mt-1 text-sm text-slate-400">Active patrol routes and basic metrics.</p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Route ID</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Officer Team</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Hotspots Covered</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Distance</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">ETA</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Priority</th>
              <th className="border-b border-slate-800 px-6 py-4 text-xs uppercase tracking-[0.3em] text-slate-500">Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((r, i) => (
              <tr key={r.id} className={`cursor-pointer border-b border-slate-800 hover:bg-slate-900/70 ${i%2===0? 'bg-slate-950/80':'bg-slate-950/60'}`} onClick={() => onSelect?.(r.id)}>
                <td className="px-6 py-4 text-white font-semibold">{r.id}</td>
                <td className="px-6 py-4 text-slate-100">{r.team}</td>
                <td className="px-6 py-4 text-slate-100">{r.hotspotsCovered.join(", ")}</td>
                <td className="px-6 py-4 text-slate-100">{r.distanceKm} km</td>
                <td className="px-6 py-4 text-slate-100">{r.eta}</td>
                <td className="px-6 py-4 text-slate-100">{r.priority}</td>
                <td className="px-6 py-4 text-slate-100">{r.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
