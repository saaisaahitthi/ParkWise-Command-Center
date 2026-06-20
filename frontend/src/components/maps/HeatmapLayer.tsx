import { useMemo } from "react";

export interface HeatmapLayerProps {
  data: Array<{ x: number; y: number; intensity: number }>;
}

export function HeatmapLayer({ data }: HeatmapLayerProps) {
  const points = useMemo(
    () =>
      data.map((entry, index) => (
        <circle
          key={index}
          cx={`${entry.x}%`}
          cy={`${entry.y}%`}
          r={12 + entry.intensity * 14}
          fill={`rgba(248,113,113,${0.12 + entry.intensity * 0.3})`}
          opacity={0.85}
        />
      )),
    [data]
  );

  return (
    <svg className="absolute inset-0 h-full w-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
      {points}
    </svg>
  );
}
