import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface WeeklyTrendDataPoint {
  day: string;
  value: number;
}

interface WeeklyTrendChartProps {
  data: WeeklyTrendDataPoint[];
}

export function WeeklyTrendChart({ data }: WeeklyTrendChartProps) {
  return (
    <div className="h-[340px] rounded-[28px] border border-slate-700 bg-slate-950/80 p-4 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 16, right: 16, left: -10, bottom: 0 }}>
          <CartesianGrid stroke="#1f2937" vertical={false} strokeDasharray="3 3" />
          <XAxis
            dataKey="day"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.18)", borderRadius: 16 }}
            labelStyle={{ color: "#cbd5e1", fontSize: 12 }}
            formatter={(value) => [`${typeof value === "number" ? value.toLocaleString("en-IN") : value ?? "0"}`, "Violations"]}
          />
          <Bar dataKey="value" radius={[12, 12, 0, 0]} fill="#38bdf8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
