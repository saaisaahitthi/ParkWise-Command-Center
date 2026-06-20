import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

interface DistributionSegment {
  name: string;
  value: number;
  color: string;
}

interface RiskDistributionChartProps {
  data: DistributionSegment[];
}

export function RiskDistributionChart({ data }: RiskDistributionChartProps) {
  return (
    <div className="h-[360px] rounded-[28px] border border-slate-700 bg-slate-950/80 p-4 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip
            contentStyle={{ background: "#0f172a", border: "1px solid rgba(148,163,184,0.18)", borderRadius: 16 }}
            formatter={(value) => [`${value ?? 0}%`, "Share"]}
            itemStyle={{ color: "#cbd5e1" }}
          />
          <Pie data={data} dataKey="value" nameKey="name" innerRadius={80} outerRadius={120} paddingAngle={4} stroke="transparent">
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Pie>
          <Legend
            layout="vertical"
            verticalAlign="middle"
            align="right"
            iconType="circle"
            wrapperStyle={{ color: "#94a3b8", fontSize: 12 }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
