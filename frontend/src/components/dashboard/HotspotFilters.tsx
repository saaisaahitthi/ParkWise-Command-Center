import { Search } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface HotspotFiltersProps {
  search: string;
  risk: string;
  zone: string;
  violations: string;
  timeWindow: string;
  onSearchChange: (value: string) => void;
  onRiskChange: (value: string) => void;
  onZoneChange: (value: string) => void;
  onViolationsChange: (value: string) => void;
  onTimeWindowChange: (value: string) => void;
}

const riskOptions = ["Critical", "High", "Medium", "Low"];
const timeWindowOptions = ["Last 1 hour", "Last 6 hours", "Last 12 hours", "Last 24 hours"];

export function HotspotFilters({
  search,
  risk,
  zone,
  violations,
  timeWindow,
  onSearchChange,
  onRiskChange,
  onZoneChange,
  onViolationsChange,
  onTimeWindowChange,
}: HotspotFiltersProps) {
  return (
    <Card className="space-y-6 rounded-4xl border-card-border p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.28em] text-slate-500">Filters</p>
          <h2 className="mt-2 text-2xl font-semibold text-white">Hotspot intelligence</h2>
        </div>
        <Badge variant="outline">Live</Badge>
      </div>

      <div className="space-y-5">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Search hotspot</p>
          <label className="mt-2 flex items-center gap-2 rounded-3xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-sm text-slate-200 focus-within:border-cyan-400">
            <Search className="h-4 w-4 text-slate-400" />
            <input
              type="search"
              value={search}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder="Search by zone, street, landmark"
              className="w-full border-none bg-transparent text-sm text-slate-100 outline-none placeholder:text-slate-500"
            />
          </label>
        </div>

        <div className="grid gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Risk level</p>
            <div className="mt-3 grid grid-cols-2 gap-3">
              {riskOptions.map((option) => (
                <button
                  key={option}
                  type="button"
                  onClick={() => onRiskChange(option)}
                  className={`rounded-3xl border px-4 py-3 text-left text-sm transition-all duration-200 ${
                    risk === option
                      ? "border-cyan-400 bg-cyan-500/10 text-white shadow-[0_0_0_1px_rgba(79,209,197,0.4)]"
                      : "border-slate-700 bg-slate-950/80 text-slate-300 hover:border-slate-500 hover:bg-slate-900"
                  }`}
                >
                  <span className="block font-semibold">{option}</span>
                  <span className="mt-1 block text-xs text-slate-400">{option === "Critical" ? "Immediate action" : option === "High" ? "Heightened risk" : option === "Medium" ? "Monitoring" : "Normal"}</span>
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Zone</p>
            <input
              type="text"
              value={zone}
              onChange={(event) => onZoneChange(event.target.value)}
              placeholder="Enter zone name"
              className="mt-3 w-full rounded-3xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 outline-none transition-colors duration-200 focus:border-cyan-400"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Violation count</p>
              <input
                type="text"
                value={violations}
                onChange={(event) => onViolationsChange(event.target.value)}
                placeholder="e.g. 50+"
                className="mt-3 w-full rounded-3xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 outline-none transition-colors duration-200 focus:border-cyan-400"
              />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Time window</p>
              <select
                value={timeWindow}
                onChange={(event) => onTimeWindowChange(event.target.value)}
                className="mt-3 w-full rounded-3xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-sm text-slate-100 outline-none transition-colors duration-200 focus:border-cyan-400"
              >
                {timeWindowOptions.map((option) => (
                  <option key={option} value={option} className="bg-slate-950 text-slate-100">
                    {option}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
