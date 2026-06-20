import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface Point { route: string; efficiency: number }
interface Props { data: Point[] }

export function RouteEfficiencyChart({ data }: Props) {
  return (
    <div className="h-36 mt-3">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 6, right: 6, left: 0, bottom: 6 }}>
          <CartesianGrid stroke="#0f172a" vertical={false} strokeDasharray="3 3" />
          <XAxis dataKey="route" axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 11 }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 11 }} width={36} />
          <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.12)", borderRadius: 12 }} />
          <Bar dataKey="efficiency" fill="#34d399" radius={[6,6,0,0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
