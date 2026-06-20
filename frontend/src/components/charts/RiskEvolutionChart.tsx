import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface RiskEvolutionDataPoint {
  label: string;
  risk: number;
}

interface RiskEvolutionChartProps {
  data: RiskEvolutionDataPoint[];
}

export function RiskEvolutionChart({ data }: RiskEvolutionChartProps) {
  return (
    <div className="h-[340px] rounded-[28px] border border-slate-700 bg-slate-950/80 p-4 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 16, right: 16, left: -10, bottom: 0 }}>
          <defs>
            <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f97316" stopOpacity={0.8} />
              <stop offset="100%" stopColor="#f97316" stopOpacity={0.08} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1f2937" vertical={false} strokeDasharray="3 3" />
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
            width={36}
          />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.18)", borderRadius: 16 }}
            labelStyle={{ color: "#cbd5e1", fontSize: 12 }}
            formatter={(value) => [`${typeof value === "number" ? value.toFixed(0) : value ?? "0"}`, "Risk"]}
          />
          <Area
            type="monotone"
            dataKey="risk"
            stroke="#f97316"
            strokeWidth={3}
            fill="url(#riskGradient)"
            activeDot={{ r: 5, fill: "#f97316" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
