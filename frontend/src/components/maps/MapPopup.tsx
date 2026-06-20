import { cn } from "@/lib/utils";

export interface MapPopupProps {
  title: string;
  description: string;
  position: { x: number; y: number };
  open?: boolean;
}

export function MapPopup({ title, description, position, open = true }: MapPopupProps) {
  if (!open) return null;

  return (
    <div
      className={cn(
        "absolute z-30 max-w-xs rounded-3xl border border-slate-700 bg-slate-950/95 p-4 shadow-[0_25px_80px_-40px_rgba(0,0,0,0.75)] text-left",
        "backdrop-blur-md"
      )}
      style={{ left: `${position.x}%`, top: `${position.y}%`, transform: "translate(-50%, -120%)" }}
    >
      <p className="text-sm font-semibold text-white">{title}</p>
      <p className="mt-2 text-sm text-slate-400">{description}</p>
    </div>
  );
}
