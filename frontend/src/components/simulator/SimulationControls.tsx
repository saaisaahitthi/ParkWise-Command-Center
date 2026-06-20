// control panel for simulator

interface Props {
  officers: number;
  setOfficers: (v: number) => void;
  vehicles: number;
  setVehicles: (v: number) => void;
  budget: number;
  setBudget: (v: number) => void;
  toggles: Record<string, boolean>;
  setToggle: (name: string, value: boolean) => void;
}

export function SimulationControls({ officers, setOfficers, vehicles, setVehicles, budget, setBudget, toggles, setToggle }: Props) {
  const toggleList = [
    { key: "festival", label: "Festival Mode" },
    { key: "rain", label: "Rain Mode" },
    { key: "concert", label: "Concert/Event" },
    { key: "vip", label: "VIP Movement" },
    { key: "closure", label: "Road Closure" },
    { key: "weekend", label: "Weekend Traffic" },
  ];

  return (
    <div className="space-y-4">
      <div className="rounded-[18px] border border-slate-700 bg-slate-950/80 p-4">
        <h4 className="text-sm font-semibold text-white">Simulation Controls</h4>

        <div className="mt-3">
          <label className="text-xs text-slate-400">Available Officers: <span className="font-semibold text-white">{officers}</span></label>
          <input type="range" min={50} max={300} value={officers} onChange={(e) => setOfficers(Number(e.target.value))} className="w-full mt-2" />
        </div>

        <div className="mt-3">
          <label className="text-xs text-slate-400">Patrol Vehicles: <span className="font-semibold text-white">{vehicles}</span></label>
          <input type="range" min={5} max={50} value={vehicles} onChange={(e) => setVehicles(Number(e.target.value))} className="w-full mt-2" />
        </div>

        <div className="mt-3">
          <label className="text-xs text-slate-400">Budget (K): <span className="font-semibold text-white">{Math.round(budget/1000)}K</span></label>
          <input type="range" min={100000} max={1000000} step={10000} value={budget} onChange={(e) => setBudget(Number(e.target.value))} className="w-full mt-2" />
        </div>

        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          {toggleList.map((t) => (
            <button key={t.key} onClick={() => setToggle(t.key, !toggles[t.key])} className={`px-3 py-2 rounded-md text-sm text-white border ${toggles[t.key] ? "border-amber-400 bg-amber-600/10" : "border-slate-700 bg-slate-900/50"}`}>
              {t.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
