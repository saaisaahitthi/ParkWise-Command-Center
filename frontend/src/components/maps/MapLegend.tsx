export interface MapLegendItem {
  label: string;
  color: string;
}

export function MapLegend({ items }: { items: MapLegendItem[] }) {
  return (
    <div className="rounded-3xl border border-slate-700 bg-slate-950/95 p-3 shadow-[0_20px_60px_-40px_rgba(0,0,0,0.65)]">
      <div className="mb-3 text-xs uppercase tracking-[0.3em] text-slate-400">Legend</div>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item.label} className="flex items-center gap-3">
            <span className="h-3.5 w-3.5 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-sm text-slate-300">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
