import { Card } from "@/components/ui/card";
import { type RouteRow } from "./RouteTable";

interface Props { route: RouteRow | null; onClose?: () => void }

export function RouteDetails({ route, onClose }: Props) {
  if (!route) return (
    <Card className="p-4">
      <h3 className="text-sm font-semibold text-white">Route details</h3>
      <p className="mt-2 text-sm text-slate-400">Select a route to view details.</p>
    </Card>
  );

  return (
    <Card className="p-4">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-semibold text-white">{route.id} — {route.team}</h3>
          <p className="mt-1 text-sm text-slate-400">Assigned officers and stop sequence.</p>
        </div>
        <div className="text-sm text-slate-400"><button onClick={onClose} className="text-slate-300">Close</button></div>
      </div>

      <div className="mt-4 grid gap-2 text-sm text-slate-200">
        <div><strong>Assigned officers:</strong> 3</div>
        <div><strong>Stops:</strong> {route.stops}</div>
        <div><strong>Stops list:</strong> {route.hotspotsCovered.join(", ")}</div>
        <div><strong>Distance:</strong> {route.distanceKm} km</div>
        <div><strong>Estimated time:</strong> {route.eta}</div>
        <div><strong>Coverage score:</strong> {route.efficiency}%</div>
      </div>
    </Card>
  );
}
