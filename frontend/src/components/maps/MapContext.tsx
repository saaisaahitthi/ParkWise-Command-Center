import * as React from "react";

export interface MapContextState {
  zoom: number;
  center: [number, number];
  theme: "dark" | "light";
}

const MapContext = React.createContext<MapContextState | undefined>(undefined);

export function MapProvider({
  children,
  value,
}: {
  children: React.ReactNode;
  value: MapContextState;
}) {
  return <MapContext.Provider value={value}>{children}</MapContext.Provider>;
}

export function useMapContainer() {
  const context = React.useContext(MapContext);
  if (!context) {
    throw new Error("useMapContainer must be used within a MapProvider");
  }
  return context;
}
