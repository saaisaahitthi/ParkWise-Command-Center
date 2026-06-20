import { cn } from "@/lib/utils";

interface HeatmapCell {
  level: "Low" | "Medium" | "High" | "Critical";
}

interface TemporalHeatmapProps {
  days: string[];
  hours: string[];
  data: HeatmapCell[][];
}

const cellStyles: Record<HeatmapCell["level"], string> = {
  Low: "bg-emerald-500/20 text-emerald-200 border-emerald-500/30",
  Medium: "bg-amber-500/15 text-amber-200 border-amber-500/25",
  High: "bg-orange-500/20 text-orange-200 border-orange-500/25",
  Critical: "bg-red-500/20 text-red-200 border-red-500/30",
};

export function TemporalHeatmap({ days, hours, data }: TemporalHeatmapProps) {
  return (
    <div className="rounded-[28px] border border-slate-700 bg-slate-950/80 p-5 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <div className="mb-5 flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-slate-500">Heatmap</p>
          <h3 className="mt-2 text-xl font-semibold text-white">Hourly congestion matrix</h3>
        </div>
        <div className="rounded-3xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-xs text-slate-300">
          Low → Critical
        </div>
      </div>

      <div className="grid gap-3 overflow-x-auto">
        <div className="grid min-w-full grid-cols-[140px_repeat(7,minmax(0,1fr))] items-center gap-2 text-xs text-slate-400">
          <div className="px-3 py-2" />
          {days.map((day) => (
            <div key={day} className="text-center uppercase tracking-[0.32em] text-slate-500">
              {day}
            </div>
          ))}
        </div>

        {hours.map((hour, rowIndex) => (
          <div key={hour} className="grid min-w-full grid-cols-[140px_repeat(7,minmax(0,1fr))] items-center gap-2">
            <div className="rounded-3xl border border-slate-700 bg-slate-950/80 px-3 py-3 text-sm font-semibold text-white">{hour}</div>
            {data[rowIndex].map((cell, cellIndex) => (
              <div
                key={`${hour}-${cellIndex}`}
                className={cn(
                  "min-h-[56px] rounded-3xl border px-3 py-3 text-center text-sm font-semibold",
                  cellStyles[cell.level]
                )}
              >
                {cell.level}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
