import { Card } from "@/components/ui/card";

const recs = [
  "Route P-07 should be extended to cover Metro Exit Gate 2.",
  "Airport Access Road coverage is below target; reassign an extra officer.",
  "MG Road Junction requires a second patrol cycle during evening rush.",
];

export function PatrolInsights() {
  return (
    <Card className="p-4">
      <h3 className="text-sm font-semibold text-white">AI recommendations</h3>
      <p className="mt-1 text-sm text-slate-400">Suggested route changes and coverage adjustments.</p>

      <ul className="mt-3 space-y-2">
        {recs.map((r, i) => (
          <li key={i} className="rounded-md border border-slate-800 bg-slate-900/60 p-3 text-sm text-slate-200">{r}</li>
        ))}
      </ul>
    </Card>
  );
}
