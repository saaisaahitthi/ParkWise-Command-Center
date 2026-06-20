import { MapPin } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMapContainer } from "./MapContext";

export interface MapMarkerProps {
  id: string;
  x: number;
  y: number;
  label: string;
  risk?: "Critical" | "High" | "Medium" | "Low";
  color?: string;
  selected?: boolean;
  onClick?: () => void;
}

const riskStyles: Record<NonNullable<MapMarkerProps["risk"]>, string> = {
  Critical: "bg-red-500 border-red-400",
  High: "bg-amber-400 border-amber-300",
  Medium: "bg-sky-400 border-sky-300",
  Low: "bg-emerald-400 border-emerald-300",
};

export function MapMarker({ x, y, label, risk = "Medium", color, selected, onClick }: MapMarkerProps) {
  const { zoom } = useMapContainer();
  const accent = color ?? riskStyles[risk];

  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      className={cn(
        "absolute flex -translate-x-1/2 -translate-y-1/2 flex-col items-center gap-2 rounded-full text-xs text-white transition-transform duration-200",
        selected ? "z-20 scale-110" : "z-10 hover:scale-105"
      )}
      style={{ left: `${x}%`, top: `${y}%`, transform: `translate(-50%, -50%) scale(${Math.min(1.2, 0.75 + zoom / 20)})` }}
    >
      <span className={cn("flex h-10 w-10 items-center justify-center rounded-full border-2 shadow-[0_0_0_6px_rgba(15,23,42,0.5)]", accent)}>
        <MapPin className="h-5 w-5 text-slate-950" />
      </span>
      <span className="rounded-full bg-slate-950/90 px-2 py-1 text-[11px] uppercase tracking-[0.24em] text-slate-300 shadow-lg shadow-slate-950/40">
        {label}
      </span>
    </button>
  );
}
