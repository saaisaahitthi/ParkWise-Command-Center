import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

interface ConfidenceGaugeProps {
  label: string;
  value: number;
  color: string;
}

export function ConfidenceGauge({ label, value, color }: ConfidenceGaugeProps) {
  return (
    <div className="rounded-[28px] border border-slate-700 bg-slate-950/80 p-4 text-center shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <div className="mb-4 text-sm uppercase tracking-[0.32em] text-slate-500">{label}</div>
      <div className="h-[170px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={[
                { name: label, value },
                { name: "rest", value: 100 - value },
              ]}
              dataKey="value"
              startAngle={180}
              endAngle={0}
              innerRadius="75%"
              outerRadius="100%"
              paddingAngle={0}
            >
              <Cell key="value" fill={color} />
              <Cell key="rest" fill="rgba(148,163,184,0.12)" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 text-3xl font-semibold text-white">{value}%</div>
    </div>
  );
}
