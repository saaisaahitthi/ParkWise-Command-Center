import { MapPin } from "lucide-react";
import { Card } from "@/components/ui/card";

export function MapPlaceholder() {
  return (
    <Card className="overflow-hidden rounded-[32px] border border-[var(--color-card-border)] p-6 shadow-[0_20px_60px_-40px_rgba(0,0,0,0.65)]">
      <div className="flex h-full min-h-[480px] flex-col justify-between rounded-[28px] border border-slate-700 bg-slate-950/80 p-10 text-slate-300 shadow-[inset_0_0_0_1px_rgba(148,163,184,0.06)]">
        <div className="flex items-center gap-3 rounded-3xl bg-slate-900/90 px-4 py-3 text-slate-100 shadow-[0_12px_30px_-18px_rgba(0,0,0,0.6)]">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-slate-800 text-sky-400">
            <MapPin className="h-5 w-5" />
          </span>
          <div>
            <p className="text-xs uppercase tracking-[0.26em] text-slate-500">Map Layer</p>
            <p className="text-sm font-semibold text-white">2024 city traffic overlay</p>
          </div>
        </div>

        <div className="flex flex-1 flex-col items-center justify-center gap-4 rounded-[28px] border-2 border-dashed border-slate-700 bg-slate-900/40 px-8 py-10 text-center">
          <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Map integration</p>
          <h2 className="max-w-md text-3xl font-display font-semibold text-white">MapMyIndia Map Coming Soon</h2>
          <p className="max-w-lg text-sm leading-7 text-slate-400">
            This placeholder represents the future live traffic layer and city patrol display. Ready for data-driven monitoring.
          </p>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          <div className="rounded-3xl bg-slate-900/80 p-4 text-sm text-slate-300">
            <span className="block text-xs uppercase tracking-[0.28em] text-slate-500">Coverage</span>
            <p className="mt-3 text-xl font-semibold text-white">47 city zones</p>
          </div>
          <div className="rounded-3xl bg-slate-900/80 p-4 text-sm text-slate-300">
            <span className="block text-xs uppercase tracking-[0.28em] text-slate-500">Alerts queued</span>
            <p className="mt-3 text-xl font-semibold text-white">112</p>
          </div>
        </div>
      </div>
    </Card>
  );
}
