import { useMemo } from "react";

export interface MapPolylineProps {
  points: Array<{ x: number; y: number }>;
  color?: string;
  width?: number;
  opacity?: number;
}

export function MapPolyline({ points, color = "#60a5fa", width = 3, opacity = 0.9 }: MapPolylineProps) {
  const path = useMemo(
    () => points.map((point) => `${point.x},${point.y}`).join(" "),
    [points]
  );

  return (
    <svg className="absolute inset-0 h-full w-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
      <polyline
        points={path}
        fill="none"
        stroke={color}
        strokeWidth={width}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={opacity}
      />
    </svg>
  );
}
