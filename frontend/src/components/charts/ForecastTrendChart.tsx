import {
  Line,
  LineChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface ForecastTrendPoint {
  day: string;
  historical: number;
  forecast: number;
}

interface ForecastTrendChartProps {
  data: ForecastTrendPoint[];
}

export function ForecastTrendChart({ data }: ForecastTrendChartProps) {
  return (
    <div className="h-[360px] rounded-[28px] border border-slate-700 bg-slate-950/80 p-4 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 16, right: 16, left: -10, bottom: 0 }}>
          <CartesianGrid stroke="#1f2937" vertical={false} strokeDasharray="3 3" />
          <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <YAxis axisLine={false} tickLine={false} tick={{ fill: "#94a3b8", fontSize: 12 }} width={36} />
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.18)", borderRadius: 16 }}
            labelStyle={{ color: "#cbd5e1", fontSize: 12 }}
            formatter={(value, name) => [`${typeof value === "number" ? value.toLocaleString("en-IN") : value}`, name as string]}
          />
          <Line
            type="monotone"
            dataKey="historical"
            name="Historical"
            stroke="#38bdf8"
            strokeWidth={3}
            dot={{ r: 3, fill: "#38bdf8" }}
            activeDot={{ r: 5, fill: "#38bdf8" }}
          />
          <Line
            type="monotone"
            dataKey="forecast"
            name="Forecast"
            stroke="#f97316"
            strokeWidth={3}
            dot={{ r: 0 }}
            strokeDasharray="6 4"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
