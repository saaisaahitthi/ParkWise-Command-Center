export interface MapHeatmapPoint {
  x: number;
  y: number;
  intensity: number;
}

export interface MapHeatmapProps {
  data: MapHeatmapPoint[];
}

export function MapHeatmap({ data }: MapHeatmapProps) {
  return (
    <svg className="absolute inset-0 h-full w-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
      {data.map((point, index) => (
        <circle
          key={`${point.x}-${point.y}-${index}`}
          cx={`${point.x}%`}
          cy={`${point.y}%`}
          r={10 + point.intensity * 10}
          fill={`rgba(248,113,113,${0.08 + point.intensity * 0.28})`}
          opacity={0.85}
        />
      ))}
    </svg>
  );
}
