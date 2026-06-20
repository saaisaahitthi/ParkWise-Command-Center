import { useEffect, useRef } from "react";
import L from "leaflet";
import { cn } from "@/lib/utils";

export interface MapMarkerItem {
  id: string;
  lat?: number;
  lng?: number;
  x: number;
  y: number;
  label: string;
  risk?: "Critical" | "High" | "Medium" | "Low";
  color?: string;
  selected?: boolean;
}

export interface MapPolylineItem {
  id: string;
  points: Array<{ x: number; y: number }>;
  route_geometry?: Array<{ lat: number; lng: number }>;
  color?: string;
}

export interface MapPopupItem {
  id: string;
  title: string;
  description: string;
  position: { x: number; y: number };
  latLng?: [number, number];
  open?: boolean;
}

export interface MapLegendItem {
  label: string;
  color: string;
}

export interface MapMyIndiaWrapperProps {
  title?: string;
  subtitle?: string;
  markers?: MapMarkerItem[];
  polylines?: MapPolylineItem[];
  heatmapData?: any[];
  popups?: MapPopupItem[];
  legendItems?: MapLegendItem[];
  onMarkerClick?: (marker: MapMarkerItem) => void;
  variant?: "default" | "patrol";
}

export function MapMyIndiaWrapper({
  title,
  subtitle,
  markers = [],
  polylines = [],
  popups = [],
  legendItems = [],
  onMarkerClick,
  variant = "default",
}: MapMyIndiaWrapperProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const polylinesLayerRef = useRef<L.LayerGroup | null>(null);

  // 1. Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Jabalpur coordinate center
    const map = L.map(mapContainerRef.current, {
      zoomControl: false,
      attributionControl: false,
    }).setView([23.1678, 79.9322], 13.5);

    // CartoDB Dark Matter premium dark tiles
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
      {
        maxZoom: 19,
      }
    ).addTo(map);

    L.control.zoom({ position: "topright" }).addTo(map);

    mapInstanceRef.current = map;
    markersLayerRef.current = L.layerGroup().addTo(map);
    polylinesLayerRef.current = L.layerGroup().addTo(map);

    return () => {
      map.remove();
      mapInstanceRef.current = null;
      markersLayerRef.current = null;
      polylinesLayerRef.current = null;
    };
  }, []);

  // 2. Synchronize Layers
  useEffect(() => {
    const map = mapInstanceRef.current;
    const markersLayer = markersLayerRef.current;
    const polylinesLayer = polylinesLayerRef.current;
    if (!map || !markersLayer || !polylinesLayer) return;

    markersLayer.clearLayers();
    polylinesLayer.clearLayers();

    // Plot pins
    markers.forEach((marker) => {
      const lat = marker.lat ?? 23.1678;
      const lng = marker.lng ?? 79.9322;
      const color = marker.color ?? "#EF4444";

      // Pulsing custom HTML pin icon
      const iconHtml = `
        <div style="position: relative; width: 14px; height: 14px;">
          <div style="
            background-color: ${color};
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 2.5px solid #000;
            box-shadow: 0 0 12px ${color};
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
          "></div>
          ${
            marker.selected
              ? `
            <div style="
              border: 2px solid ${color};
              width: 26px;
              height: 26px;
              border-radius: 50%;
              position: absolute;
              top: 50%;
              left: 50%;
              transform: translate(-50%, -50%);
              animation: map-pulse 1.8s infinite ease-out;
            "></div>
          `
              : ""
          }
        </div>
      `;

      const customIcon = L.divIcon({
        html: iconHtml,
        className: "",
        iconSize: [26, 26],
        iconAnchor: [13, 13],
      });

      const lfMarker = L.marker([lat, lng], { icon: customIcon }).addTo(
        markersLayer
      );

      // Attach tooltip
      lfMarker.bindTooltip(marker.label, {
        permanent: true,
        direction: "top",
        offset: [0, -14],
        className:
          "bg-slate-950/95 border border-slate-800 text-slate-200 text-[10px] font-bold uppercase tracking-wider rounded-full px-2.5 py-0.5 shadow-lg pointer-events-none select-none",
      });

      if (onMarkerClick) {
        lfMarker.on("click", () => {
          onMarkerClick(marker);
        });
      }
    });

    // Plot polyline paths
    polylines.forEach((poly) => {
      const coords = poly.route_geometry
        ? poly.route_geometry.map((pt) => [pt.lat, pt.lng] as L.LatLngExpression)
        : [];

      if (coords.length > 0) {
        L.polyline(coords, {
          color: poly.color ?? "#60a5fa",
          weight: 4.5,
          opacity: 0.85,
        }).addTo(polylinesLayer);
      }
    });

    // Close any previous popups
    map.closePopup();

    // Render active popups
    popups.forEach((popup) => {
      const position = popup.latLng ?? [23.1678, 79.9322];
      if (popup.open) {
        L.popup({
          closeButton: false,
          offset: [0, -5],
          className: "leaflet-custom-popup",
        })
          .setLatLng(position)
          .setContent(
            `
            <div style="font-family: sans-serif; font-size: 12px; color: #fff; padding: 4px; line-height: 1.4;">
              <strong style="display: block; font-size: 13px; color: #67e8f9; font-weight: bold; margin-bottom: 2px;">${popup.title}</strong>
              <span style="color: #cbd5e1; font-weight: 500;">${popup.description}</span>
            </div>
          `
          )
          .openOn(map);
      }
    });

    // Center map view automatically
    const selected = markers.find((m) => m.selected);
    if (selected && selected.lat && selected.lng) {
      map.setView([selected.lat, selected.lng], 14.5, { animate: true });
    } else if (markers.length > 0) {
      const bounds = L.latLngBounds(
        markers.map((m) => [m.lat ?? 23.1678, m.lng ?? 79.9322])
      );
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [markers, polylines, popups]);

  return (
    <div
      className={cn(
        "border border-[var(--color-card-border)] bg-[var(--color-card-bg)] shadow-[0_20px_60px_-40px_rgba(0,0,0,0.65)]",
        variant === "patrol"
          ? "overflow-hidden rounded-[28px]"
          : "rounded-[32px]"
      )}
    >
      <div
        className={cn(
          "border-b border-[var(--color-card-border)] p-5",
          variant === "patrol"
            ? "flex flex-col gap-4 bg-[linear-gradient(120deg,rgba(15,29,41,0.9),rgba(8,17,27,0.7))] sm:flex-row sm:items-center sm:justify-between"
            : "flex items-center justify-between"
        )}
      >
        <div className="min-w-0">
          {title ? (
            <h3
              className={cn(
                "text-lg font-semibold text-white",
                variant === "patrol" && "tracking-tight"
              )}
            >
              {title}
            </h3>
          ) : null}
          {subtitle ? (
            <p
              className={cn(
                "mt-1 text-sm text-slate-400",
                variant === "patrol" && "max-w-2xl leading-5"
              )}
            >
              {subtitle}
            </p>
          ) : null}
        </div>

        {/* Legend */}
        <div
          className={cn(
            "flex items-center text-xs font-semibold text-slate-400",
            variant === "patrol"
              ? "w-fit flex-wrap gap-1 rounded-2xl border border-white/[0.07] bg-black/20 p-1.5 shadow-inner shadow-black/20"
              : "gap-4 rounded-2xl border border-slate-800 bg-slate-900/40 px-3.5 py-2"
          )}
        >
          {legendItems.map((legend) => (
            <div
              key={legend.label}
              className={cn(
                "flex items-center",
                variant === "patrol"
                  ? "gap-2 rounded-xl border border-transparent bg-white/[0.035] px-3 py-2 transition hover:border-cyan-300/10 hover:bg-cyan-300/[0.06] hover:text-slate-200"
                  : "gap-1.5"
              )}
            >
              <span
                className={cn(
                  "rounded-full",
                  variant === "patrol"
                    ? "h-2.5 w-2.5 border border-white/20 shadow-[0_0_10px_currentColor]"
                    : "h-2 w-2"
                )}
                style={{
                  backgroundColor: legend.color,
                  ...(variant === "patrol" ? { color: legend.color } : {}),
                }}
              />
              <span>{legend.label}</span>
            </div>
          ))}
        </div>
      </div>

      <div
        className={cn(
          "relative overflow-hidden bg-slate-950/80",
          variant === "patrol"
            ? "min-h-[440px] shadow-[inset_0_0_0_1px_rgba(148,163,184,0.04)]"
            : "min-h-[420px] rounded-b-[32px]"
        )}
      >
        <div
          ref={mapContainerRef}
          className="absolute inset-0 h-full w-full z-10"
        />
      </div>
    </div>
  );
}
