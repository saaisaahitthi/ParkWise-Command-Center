import { ChevronLeft, ChevronRight, Plus, Minus } from "lucide-react";
import { Button } from "@/components/ui/button";

export interface MapControlsProps {
  onZoomIn?: () => void;
  onZoomOut?: () => void;
  onPanLeft?: () => void;
  onPanRight?: () => void;
  zoomLevel?: number;
}

export function MapControls({ onZoomIn, onZoomOut, onPanLeft, onPanRight, zoomLevel }: MapControlsProps) {
  return (
    <div className="flex flex-col gap-2 rounded-3xl border border-slate-700 bg-slate-950/95 p-3 shadow-[0_20px_60px_-40px_rgba(0,0,0,0.65)]">
      <div className="flex items-center justify-between gap-2 text-xs uppercase tracking-[0.28em] text-slate-400">Controls</div>
      <div className="grid grid-cols-2 gap-2">
        <Button type="button" variant="outline" size="sm" onClick={onZoomIn}>
          <Plus className="h-4 w-4" />
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={onZoomOut}>
          <Minus className="h-4 w-4" />
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={onPanLeft}>
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <Button type="button" variant="outline" size="sm" onClick={onPanRight}>
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
      {typeof zoomLevel === "number" ? (
        <div className="rounded-3xl bg-slate-900 px-3 py-2 text-sm text-slate-300">Zoom {zoomLevel}x</div>
      ) : null}
    </div>
  );
}
