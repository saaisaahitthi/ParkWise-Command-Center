import { Users, MapPin, Clock3, AlertTriangle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { HotspotRecord } from "@/components/dashboard/HotspotTable";

const riskBadgeMap: Record<HotspotRecord["risk"], "critical" | "high" | "medium" | "low"> = {
  Critical: "critical",
  High: "high",
  Medium: "medium",
  Low: "low",
};

interface HotspotDetailsDrawerProps {
  hotspot?: HotspotRecord;
  onClose: () => void;
}

export function HotspotDetailsDrawer({ hotspot, onClose }: HotspotDetailsDrawerProps) {
  if (!hotspot) {
    return (
      <Card className="rounded-4xl border-card-border p-6">
        <div className="space-y-3">
          <p className="text-sm uppercase tracking-[0.28em] text-slate-500">Hotspot details</p>
          <h2 className="text-2xl font-semibold text-white">Select a hotspot</h2>
          <p className="text-sm leading-6 text-slate-400">Open a hotspot from the table or map to review details and tactical guidance.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="rounded-4xl border-card-border p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm uppercase tracking-[0.28em] text-slate-500">Hotspot overview</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">{hotspot.name}</h2>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded-full border border-slate-700 bg-slate-950/90 px-3 py-2 text-sm text-slate-300 transition hover:border-slate-500 hover:text-white"
        >
          Close
        </button>
      </div>

      <div className="mt-6 space-y-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Risk level</p>
            <div className="mt-3 flex items-center gap-2">
              <Badge variant={riskBadgeMap[hotspot.risk]}>{hotspot.risk}</Badge>
              <span className="text-sm text-slate-300">{hotspot.violations} violations</span>
            </div>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Recommended officers</p>
            <p className="mt-3 text-3xl font-semibold text-white">{hotspot.officers}</p>
            <p className="text-sm text-slate-400">Deploy enforcement units and mobile patrols.</p>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
            <div className="flex items-center gap-2 text-slate-300">
              <Clock3 className="h-4 w-4 text-cyan-300" />
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Peak hours</p>
            </div>
            <p className="mt-3 text-lg font-semibold text-white">{hotspot.peakHour}</p>
          </div>
          <div className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
            <div className="flex items-center gap-2 text-slate-300">
              <AlertTriangle className="h-4 w-4 text-amber-300" />
              <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Forecasted risk</p>
            </div>
            <p className="mt-3 text-lg font-semibold text-white">{hotspot.risk === "Critical" ? "Very high" : hotspot.risk === "High" ? "Elevated" : hotspot.risk === "Medium" ? "Moderate" : "Low"}</p>
          </div>
        </div>

        <div className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
          <div className="flex items-center gap-2 text-slate-300">
            <MapPin className="h-4 w-4 text-cyan-300" />
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Coordinates</p>
          </div>
          <p className="mt-3 text-sm text-slate-100">{hotspot.id.replace("hotspot-", "")}</p>
        </div>

        <div className="rounded-3xl border border-slate-700 bg-slate-950/80 p-4">
          <div className="flex items-center gap-2 text-slate-300">
            <Users className="h-4 w-4 text-cyan-300" />
            <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Tactical guidance</p>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-400">
            Maintain mobile enforcement within the hotspot and coordinate with local traffic signal teams to reduce congestion during peak hours.
          </p>
        </div>
      </div>
    </Card>
  );
}
