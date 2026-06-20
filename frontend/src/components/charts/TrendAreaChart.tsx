import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface TrendDataPoint {
  label: string;
  value: number;
}

interface TrendAreaChartProps {
  data: TrendDataPoint[];
}

export function TrendAreaChart({ data }: TrendAreaChartProps) {
  return (
    <div className="mt-6 h-[320px]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 12, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#38BDF8" stopOpacity={0.75} />
              <stop offset="100%" stopColor="#38BDF8" stopOpacity={0.08} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1f2937" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            width={40}
            tickFormatter={(value) => `${value / 1000}k`}
          />
          <Tooltip
            contentStyle={{
              background: "#0f172a",
              border: "1px solid rgba(148,163,184,0.18)",
              borderRadius: 16,
            }}
            labelStyle={{ color: "#cbd5e1", fontSize: 12 }}
            formatter={(value) => [`${typeof value === "number" ? value.toLocaleString("en-IN") : value ?? "0"}`, "Violations"]}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#38BDF8"
            strokeWidth={3}
            fill="url(#trendGradient)"
            activeDot={{ r: 5, fill: "#38BDF8" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
