import { Zap } from "lucide-react";
import { Card } from "@/components/ui/card";

const hotspots = [
  { zone: "MG Road Junction", score: 98, change: "+14%" },
  { zone: "Electronic City Exit", score: 91, change: "+11%" },
  { zone: "Hebbal Flyover", score: 87, change: "+8%" },
  { zone: "Airport Road", score: 83, change: "+5%" },
  { zone: "Koramangala Hub", score: 79, change: "+3%" },
];

export function HotspotRanking() {
  return (
    <Card className="rounded-[32px] border border-[var(--color-card-border)] p-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Hotspot ranking</p>
          <h2 className="mt-2 text-xl font-semibold text-white">Highest risk zones</h2>
        </div>
        <div className="inline-flex items-center gap-2 rounded-2xl bg-slate-900/80 px-3 py-2 text-sm text-slate-300">
          <Zap className="h-5 w-5 text-amber-400" />
          Live
        </div>
      </div>

      <div className="mt-6 space-y-4">
        {hotspots.map((item) => (
          <div key={item.zone} className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-semibold text-white">{item.zone}</p>
                <p className="text-xs text-slate-500">Risk score {item.score}</p>
              </div>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-300">
                {item.change}
              </span>
            </div>
            <div className="mt-3 h-2.5 overflow-hidden rounded-full bg-slate-900">
              <div
                className="h-2.5 rounded-full bg-gradient-to-r from-orange-400 to-rose-500"
                style={{ width: `${item.score}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
