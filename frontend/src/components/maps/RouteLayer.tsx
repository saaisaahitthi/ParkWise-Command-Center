// RouteLayer uses SVG polyline rendering directly.

export interface RouteLayerProps {
  routes: Array<{ points: Array<{ x: number; y: number }>; color: string }>;
}

export function RouteLayer({ routes }: RouteLayerProps) {
  return (
    <svg className="absolute inset-0 h-full w-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
      {routes.map((route, index) => (
        <polyline
          key={index}
          points={route.points.map((point) => `${point.x},${point.y}`).join(" ")}
          fill="none"
          stroke={route.color}
          strokeWidth={2.5}
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity={0.9}
        />
      ))}
    </svg>
  );
}
