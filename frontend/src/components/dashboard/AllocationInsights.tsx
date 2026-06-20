import { Card } from "@/components/ui/card";

const recommendations = [
  "Deploy 4 additional officers to MG Road Junction.",
  "Reduce deployment at Airport Access Road by 2 officers.",
  "Increase patrol frequency near Metro Exit Gate 2.",
  "Stage a rapid response team near Railway Station Circle during peak hours.",
];

export function AllocationInsights() {
  return (
    <Card className="p-4">
      <h3 className="text-sm font-semibold text-white">AI recommendations</h3>
      <p className="mt-1 text-sm text-slate-400">Actionable recommendations based on simulated forecasts.</p>

      <ul className="mt-3 space-y-2">
        {recommendations.map((r, i) => (
          <li key={i} className="rounded-md border border-slate-800 bg-slate-900/60 p-3 text-sm text-slate-200">{r}</li>
        ))}
      </ul>
    </Card>
  );
}
