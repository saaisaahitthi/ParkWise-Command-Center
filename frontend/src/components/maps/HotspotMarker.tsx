import { MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

export interface HotspotMarkerProps {
  label: string;
  risk: "Critical" | "High" | "Medium" | "Low";
  x: number;
  y: number;
  selected?: boolean;
  onClick?: () => void;
}

const markerStyles: Record<HotspotMarkerProps["risk"], string> = {
  Critical: "bg-red-500 border-red-400",
  High: "bg-amber-400 border-amber-300",
  Medium: "bg-sky-400 border-sky-300",
  Low: "bg-emerald-400 border-emerald-300",
};

export function HotspotMarker({ label, risk, x, y, selected, onClick }: HotspotMarkerProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-2 rounded-full text-xs text-white transition duration-200",
        selected ? "z-20 scale-110" : "z-10 hover:scale-105"
      )}
      style={{ left: `${x}%`, top: `${y}%` }}
    >
      <span className={cn("flex h-10 w-10 items-center justify-center rounded-full border-2 shadow-lg shadow-slate-950/40", markerStyles[risk])}>
        <MapPin className="h-5 w-5" />
      </span>
      <span className="rounded-full bg-slate-950/90 px-2 py-1 text-[11px] uppercase tracking-[0.25em] text-slate-300 shadow-lg shadow-slate-950/30">
        {label}
      </span>
    </button>
  );
}
