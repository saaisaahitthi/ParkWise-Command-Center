import {
  Line,
  LineChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface HourlyTrendDataPoint {
  hour: string;
  value: number;
}

interface HourlyTrendChartProps {
  data: HourlyTrendDataPoint[];
}

export function HourlyTrendChart({ data }: HourlyTrendChartProps) {
  return (
    <div className="h-[340px] rounded-[28px] border border-slate-700 bg-slate-950/80 p-4 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 16, right: 18, left: -12, bottom: 0 }}>
          <defs>
            <linearGradient id="hourlyGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4fd1c5" stopOpacity={0.85} />
              <stop offset="100%" stopColor="#4fd1c5" stopOpacity={0.12} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1f2937" vertical={false} strokeDasharray="3 3" />
          <XAxis
            dataKey="hour"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            minTickGap={12}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={40}
            tickFormatter={(value) => `${value}`}
          />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.18)", borderRadius: 16 }}
            labelStyle={{ color: "#cbd5e1", fontSize: 12 }}
            formatter={(value) => [`${typeof value === "number" ? value.toLocaleString("en-IN") : value ?? "0"}`, "Violations"]}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#4fd1c5"
            strokeWidth={3}
            dot={{ r: 3, stroke: "#ffffff", strokeWidth: 2, fill: "#4fd1c5" }}
            activeDot={{ r: 5, fill: "#4fd1c5" }}
            fill="url(#hourlyGradient)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
