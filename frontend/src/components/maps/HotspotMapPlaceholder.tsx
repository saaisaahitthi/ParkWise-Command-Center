import { MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

export type HotspotMarker = {
  id: string;
  label: string;
  risk: "Critical" | "High" | "Medium" | "Low";
  left: string;
  top: string;
  violations: number;
};

const riskStyles: Record<string, string> = {
  Critical: "bg-red-500/90 border-red-400",
  High: "bg-orange-400/90 border-orange-300",
  Medium: "bg-amber-300/95 border-amber-200",
  Low: "bg-emerald-400/95 border-emerald-300",
};

interface HotspotMapPlaceholderProps {
  markers: HotspotMarker[];
  selectedId?: string;
  onSelect: (id: string) => void;
}

export function HotspotMapPlaceholder({ markers, selectedId, onSelect }: HotspotMapPlaceholderProps) {
  return (
    <div className="rounded-4xl border border-card-border bg-card-bg shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)] p-5">
      <div className="mb-4 flex items-center justify-between gap-3 rounded-3xl border border-slate-700 bg-slate-950/70 px-4 py-3 text-sm text-slate-300">
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-slate-500">Map layer</p>
          <p className="mt-1 text-sm font-semibold text-white">2024 hotspot traffic overview</p>
        </div>
        <span className="inline-flex items-center gap-2 rounded-full bg-slate-900/70 px-3 py-2 text-xs uppercase tracking-[0.28em] text-slate-400">
          <MapPin className="h-4 w-4 text-cyan-300" />
          MapMyIndia Hotspot Map
        </span>
      </div>

      <div className="relative overflow-hidden rounded-[28px] border border-slate-800 bg-linear-to-br from-slate-950 via-slate-900 to-slate-900 px-4 py-6 shadow-inner shadow-slate-950/40">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(79,209,197,0.18),transparent_32%),radial-gradient(circle_at_bottom_right,rgba(59,130,246,0.14),transparent_30%)]" />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(255,255,255,0.04)_1px,transparent_1px),linear-gradient(rgba(255,255,255,0.04)_1px,transparent_1px)] bg-size-[80px_80px] opacity-30" />
        <div className="relative min-h-105">
          <div className="pointer-events-none absolute inset-0 rounded-[28px] border border-dashed border-slate-700 opacity-60" />

          {markers.map((marker) => {
            const active = selectedId === marker.id;
            return (
              <button
                key={marker.id}
                type="button"
                onClick={() => onSelect(marker.id)}
                className={cn(
                  "absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-2 rounded-full text-xs text-slate-100 transition-all duration-200",
                  active ? "z-20" : "z-10 hover:scale-105"
                )}
                style={{ left: marker.left, top: marker.top }}
              >
                <span
                  className={cn(
                    "flex h-10 w-10 items-center justify-center rounded-full border-2 shadow-[0_0_0_3px_rgba(15,23,42,0.55)]",
                    riskStyles[marker.risk]
                  )}
                >
                  <MapPin className="h-5 w-5 text-slate-950" />
                </span>
                <span className="max-w-27.5 rounded-full bg-slate-950/90 px-2 py-1 text-[11px] uppercase tracking-[0.23em] text-slate-300 shadow-lg shadow-slate-950/30">
                  {marker.risk}
                </span>
              </button>
            );
          })}
        </div>

        <div className="mt-5 grid gap-3 sm:grid-cols-3">
          <div className="rounded-3xl border border-slate-700 bg-slate-950/80 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Coverage</p>
            <p className="mt-2 text-lg font-semibold text-white">47 active zones</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/80 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Alerts queued</p>
            <p className="mt-2 text-lg font-semibold text-white">112</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/80 px-4 py-3">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Live flow</p>
            <p className="mt-2 text-lg font-semibold text-white">High</p>
          </div>
        </div>
      </div>
    </div>
  );
}
