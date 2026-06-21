import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

interface RiskSegment {
  name: string;
  value: number;
  color: string;
}

interface RiskDonutChartProps {
  data: RiskSegment[];
}

export function RiskDonutChart({ data }: RiskDonutChartProps) {
  const total = data.reduce((sum, segment) => sum + segment.value, 0);
  const priorityCount = data
    .filter((segment) => segment.name !== "Low")
    .reduce((sum, segment) => sum + segment.value, 0);
  const percentage = (value: number) =>
    total > 0 ? (value / total) * 100 : 0;
  const formatPercentage = (value: number) => {
    const result = percentage(value);
    return result > 0 && result < 0.1 ? "<0.1%" : `${result.toFixed(1)}%`;
  };

  return (
    <div className="grid min-h-[250px] grid-cols-[minmax(130px,0.9fr)_minmax(150px,1.1fr)] items-center gap-2">
      <div className="relative h-[210px] min-w-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip
              contentStyle={{
                background: "#0f172a",
                border: "1px solid rgba(148,163,184,0.18)",
                borderRadius: 14,
              }}
              formatter={(value, _name, item) => {
                const count = Number(value ?? 0);
                return [
                  `${count.toLocaleString("en-IN")} · ${formatPercentage(count)}`,
                  item.payload.name,
                ];
              }}
              itemStyle={{ color: "#cbd5e1" }}
            />
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={52}
              outerRadius={80}
              minAngle={2}
              stroke="#08111b"
              strokeWidth={2}
              paddingAngle={1}
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-[9px] font-semibold uppercase tracking-[0.16em] text-slate-500">
            Priority share
          </span>
          <span className="mt-1 font-mono text-xl font-bold text-white">
            {formatPercentage(priorityCount)}
          </span>
        </div>
      </div>

      <div className="space-y-2">
        {data.map((segment) => (
          <div
            key={segment.name}
            className="flex items-center justify-between gap-3 rounded-xl border border-white/[0.055] bg-black/15 px-2.5 py-2"
          >
            <span className="flex min-w-0 items-center gap-2 text-[10px] font-semibold text-slate-300">
              <span
                className="h-2 w-2 shrink-0 rounded-full shadow-[0_0_8px_currentColor]"
                style={{ backgroundColor: segment.color, color: segment.color }}
              />
              {segment.name}
            </span>
            <span className="whitespace-nowrap font-mono text-[9px] text-slate-500">
              <strong className="font-semibold text-slate-300">
                {formatPercentage(segment.value)}
              </strong>
              {" · "}
              {segment.value.toLocaleString("en-IN")}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
