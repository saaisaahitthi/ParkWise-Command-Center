import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { type AllocationRow } from "@/components/dashboard/OfficerAllocationTable";

interface Props { rows: AllocationRow[] }

export function OfficerDistributionChart({ rows }: Props) {
  const data = rows.map((r) => ({ zone: r.hotspot, officers: r.allocatedOfficers }));

  return (
    <div className="h-48 mt-3">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 6, right: 8, left: 0, bottom: 6 }}>
          <CartesianGrid stroke="#111827" vertical={false} strokeDasharray="3 3" />
          <XAxis dataKey="zone" axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 11 }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 11 }} width={36} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.12)", borderRadius: 12 }} />
          <Bar dataKey="officers" fill="#60a5fa" radius={[6,6,0,0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
