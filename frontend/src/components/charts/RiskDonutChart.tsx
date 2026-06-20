import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import type { RiskChartSegment } from "@/types/views";

interface RiskDonutChartProps {
  data: RiskChartSegment[];
}

export function RiskDonutChart({ data }: RiskDonutChartProps) {
  return (
    <div className="mt-6 h-[320px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip
            contentStyle={{
              background: "#0f172a",
              border: "1px solid rgba(148,163,184,0.18)",
              borderRadius: 16,
            }}
            formatter={(value) => [`${value ?? 0}%`, "Exposure"]}
            itemStyle={{ color: "#cbd5e1" }}
          />
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={72}
            outerRadius={110}
            stroke="transparent"
            paddingAngle={4}
          >
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
