interface Scenario {
  id: string;
  label: string;
  officers: number;
  vehicles: number;
  budget: number;
  toggles?: Record<string, boolean>;
}

interface Props { onApply: (s: Scenario) => void }

const scenarios: Scenario[] = [
  { id: "festival", label: "Festival Night", officers: 220, vehicles: 28, budget: 500000, toggles: { festival: true, weekend: true } },
  { id: "weekend", label: "Weekend Rush", officers: 150, vehicles: 18, budget: 220000, toggles: { weekend: true } },
  { id: "airport", label: "Airport Event", officers: 180, vehicles: 20, budget: 300000, toggles: { vip: true } },
  { id: "metro", label: "Metro Breakdown", officers: 200, vehicles: 24, budget: 350000, toggles: { concert: true } },
  { id: "rally", label: "Political Rally", officers: 260, vehicles: 30, budget: 600000, toggles: { closure: true, festival: true } },
];

export function ScenarioCards({ onApply }: Props) {
  return (
    <div className="space-y-3">
      <h4 className="text-sm font-semibold text-white">Scenarios</h4>
      <div className="grid gap-2 sm:grid-cols-2">
        {scenarios.map((s) => (
          <button key={s.id} onClick={() => onApply(s)} className="rounded-md border border-slate-700 bg-slate-900/60 px-3 py-2 text-left text-sm text-slate-200">
            <div className="font-semibold text-white">{s.label}</div>
            <div className="text-xs text-slate-400 mt-1">Officers: {s.officers} • Vehicles: {s.vehicles}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
