import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

interface Props { label: string; value: number; color?: string }

export function CoverageChart({ label, value, color = "#4fd1c5" }: Props) {
  const data = [ { name: label, value }, { name: "rest", value: Math.max(0, 100 - value) } ];

  return (
    <div className="h-28 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={data} dataKey="value" startAngle={180} endAngle={0} innerRadius={48} outerRadius={64} paddingAngle={0}>
            <Cell key="value" fill={color} />
            <Cell key="rest" fill="rgba(148,163,184,0.12)" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-2 text-sm text-slate-300">{label}: <span className="font-semibold text-white">{value}%</span></div>
    </div>
  );
}
