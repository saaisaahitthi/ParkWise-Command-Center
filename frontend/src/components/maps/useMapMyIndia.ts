import { useCallback, useState } from "react";

export function useMapMyIndia(
  initialZoom = 11,
  initialCenter: [number, number] = [12.97, 77.59]
) {
  const [zoom, setZoom] = useState(initialZoom);
  const [center, setCenter] = useState<[number, number]>(initialCenter);

  const zoomIn = useCallback(() => setZoom((value) => Math.min(20, value + 1)), []);
  const zoomOut = useCallback(() => setZoom((value) => Math.max(1, value - 1)), []);
  const panLeft = useCallback(() => setCenter(([lng, lat]) => [lng - 0.02, lat]), []);
  const panRight = useCallback(() => setCenter(([lng, lat]) => [lng + 0.02, lat]), []);
  const panUp = useCallback(() => setCenter(([lng, lat]) => [lng, lat + 0.02]), []);
  const panDown = useCallback(() => setCenter(([lng, lat]) => [lng, lat - 0.02]), []);

  return {
    zoom,
    center,
    setZoom,
    setCenter,
    zoomIn,
    zoomOut,
    panLeft,
    panRight,
    panUp,
    panDown,
  };
}
