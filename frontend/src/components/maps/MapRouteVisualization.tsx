import { MapPolyline } from "./MapPolyline";
import { MapMarker } from "./MapMarker";

export interface MapRouteVisualizationProps {
  routes: Array<{
    id: string;
    points: Array<{ x: number; y: number }>;
    color?: string;
    label: string;
  }>;
  selectedRouteId?: string;
  onSelectRoute?: (id: string) => void;
}

export function MapRouteVisualization({ routes, selectedRouteId, onSelectRoute }: MapRouteVisualizationProps) {
  return (
    <div className="absolute inset-0">
      {routes.map((route) => (
        <MapPolyline key={route.id} points={route.points} color={route.color} />
      ))}
      {routes.map((route) => (
        <MapMarker
          key={`${route.id}-start`}
          id={`${route.id}-start`}
          x={route.points[0]?.x ?? 0}
          y={route.points[0]?.y ?? 0}
          label={route.label}
          color={route.color}
          selected={selectedRouteId === route.id}
          onClick={() => onSelectRoute?.(route.id)}
        />
      ))}
    </div>
  );
}
