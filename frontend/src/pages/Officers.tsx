import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle,
  MapPin,
  Shield,
  SlidersHorizontal,
  Users,
} from "lucide-react";
import { PageHeader } from "@/layout/PageHeader";
import { Card } from "@/components/ui/card";
import {
  computeAllocation,
  fetchLatestAllocation,
} from "@/services/officers";
import { getLocationDisplayName } from "@/data/dashboardPresentationData";

export default function OfficersPage() {
  const [totalOfficersInput, setTotalOfficersInput] = useState(20);
  const [topNHotspotsInput, setTopNHotspotsInput] = useState(4);
  const [updated, setUpdated] = useState(false);

  // Fetch latest allocation data
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["allocation-latest"],
    queryFn: fetchLatestAllocation,
    refetchInterval: 10000,
  });

  // Recompute allocation mutation
  const computeMutation = useMutation({
    mutationFn: () =>
      computeAllocation({
        total_officers: totalOfficersInput,
        top_n_hotspots: topNHotspotsInput,
      }),
    onSuccess: () => {
      setUpdated(true);
      refetch();
      setTimeout(() => setUpdated(false), 3000);
    },
  });

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-cyan-400" />
          <p className="text-sm font-semibold">Generating resource distribution schedules...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="rounded-3xl border border-red-900 bg-red-950/20 p-8 text-center text-red-300">
        <AlertTriangle className="mx-auto h-12 w-12 mb-3 text-red-500 animate-pulse" />
        <h3 className="text-lg font-semibold text-white">Allocation Stream Disconnected</h3>
        <p className="mt-2 text-sm text-slate-400">
          Verify backend connectivity at <code className="text-red-200">http://127.0.0.1:8000/api/v1</code> or toggle header Mode to Mock.
        </p>
      </div>
    );
  }

  const { total_officers_allocated, hotspots_covered, allocations = [] } = data;

  return (
    <div className="space-y-4 pb-6">
      <PageHeader
        eyebrow="Field Allocation"
        title="Officer Allocation"
        description="Assign enforcement units across priority hotspots based on current and forecasted risk."
      />

      <div className="grid gap-3 sm:grid-cols-2">
        {[
          {
            label: "Total Officers Deployed",
            value: total_officers_allocated,
            icon: Users,
            tone: "text-cyan-200",
          },
          {
            label: "Hotspots Covered",
            value: hotspots_covered,
            icon: MapPin,
            tone: "text-amber-200",
          },
        ].map(({ label, value, icon: Icon, tone }) => (
          <Card
            key={label}
            className="relative overflow-hidden rounded-[22px] border-cyan-300/[0.09] bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.08),transparent_38%),linear-gradient(150deg,rgba(14,27,39,0.96),rgba(7,15,24,0.9))] p-4 shadow-[0_22px_60px_-48px_rgba(34,211,238,0.85)]"
          >
            <div className="pointer-events-none absolute -right-10 -top-10 h-24 w-24 rounded-full border border-cyan-300/[0.07]" />
            <div className="relative flex items-center gap-3">
              <span
                className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-current/15 bg-white/[0.035] ${tone}`}
              >
                <Icon className="h-4 w-4" />
              </span>
              <div>
                <p className="text-[9px] font-semibold uppercase tracking-[0.17em] text-slate-500">
                  {label}
                </p>
                <p className="mt-1 font-mono text-xl font-bold tracking-tight text-white">
                  {value}
                </p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid items-start gap-4 xl:grid-cols-[280px_minmax(0,1fr)]">
        <Card className="relative h-fit overflow-hidden rounded-[24px] border-cyan-300/[0.1] bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.1),transparent_38%),linear-gradient(150deg,rgba(14,27,39,0.96),rgba(7,15,24,0.9))] p-4 shadow-[0_24px_70px_-50px_rgba(34,211,238,0.9)]">
          <div className="pointer-events-none absolute -right-12 -top-12 h-28 w-28 rounded-full border border-cyan-300/[0.08]" />
          <div className="relative">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-300/15 bg-cyan-300/[0.07] text-cyan-200">
              <SlidersHorizontal className="h-4 w-4" />
            </span>
            <p className="mt-4 text-[9px] font-semibold uppercase tracking-[0.24em] text-cyan-300/70">
              Deployment Parameters
            </p>
            <h2 className="mt-1 text-base font-semibold text-white">
              Allocation Controls
            </h2>
            <p className="mt-1.5 text-xs leading-5 text-slate-500">
              Adjust available units and the number of priority hotspots used
              for allocation.
            </p>
          </div>

          <div className="relative mt-5 space-y-5">
            <label className="block">
              <span className="flex items-center justify-between gap-3 text-[11px] font-semibold text-slate-300">
                Total available officers
                <span className="rounded-lg border border-cyan-300/15 bg-cyan-300/[0.06] px-2 py-1 font-mono text-cyan-200">
                  {totalOfficersInput}
                </span>
              </span>
              <input
                type="range"
                min="5"
                max="100"
                step="5"
                value={totalOfficersInput}
                onChange={(e) => setTotalOfficersInput(Number(e.target.value))}
                className="mt-3 h-1.5 w-full cursor-pointer accent-cyan-300"
              />
            </label>

            <label className="block">
              <span className="flex items-center justify-between gap-3 text-[11px] font-semibold text-slate-300">
                Target top hotspots
                <span className="rounded-lg border border-cyan-300/15 bg-cyan-300/[0.06] px-2 py-1 font-mono text-cyan-200">
                  {topNHotspotsInput}
                </span>
              </span>
              <input
                type="range"
                min="2"
                max="10"
                step="1"
                value={topNHotspotsInput}
                onChange={(e) => setTopNHotspotsInput(Number(e.target.value))}
                className="mt-3 h-1.5 w-full cursor-pointer accent-cyan-300"
              />
            </label>

            <button
              type="button"
              onClick={() => computeMutation.mutate()}
              disabled={computeMutation.isPending}
              className="flex h-10 w-full cursor-pointer items-center justify-center gap-2 rounded-xl border border-cyan-300/20 bg-cyan-300/[0.08] px-3 text-xs font-semibold text-cyan-100 shadow-[0_12px_30px_-20px_rgba(34,211,238,0.85)] transition hover:border-cyan-300/30 hover:bg-cyan-300/[0.12] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {computeMutation.isPending ? (
                <div className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-cyan-300 border-t-transparent" />
              ) : updated ? (
                <CheckCircle className="h-3.5 w-3.5 text-emerald-300" />
              ) : (
                <Shield className="h-3.5 w-3.5" />
              )}
              <span>
                {updated ? "Allocation Applied!" : "Optimize Allocations"}
              </span>
            </button>
          </div>
        </Card>

        <Card className="overflow-hidden rounded-[26px] border-cyan-300/[0.08] bg-[linear-gradient(145deg,rgba(14,27,39,0.94),rgba(8,17,27,0.84))] p-0 shadow-[0_28px_80px_-58px_rgba(34,211,238,0.6)]">
          <div className="flex flex-col gap-3 border-b border-white/[0.06] px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-[9px] font-semibold uppercase tracking-[0.22em] text-cyan-300/65">
                Deployment priorities
              </p>
              <h2 className="mt-1 text-base font-semibold text-white">
                Officer Deployment Plan
              </h2>
              <p className="mt-0.5 text-[10px] text-slate-500">
                Current unit distribution across ranked hotspots
              </p>
            </div>
            <span className="flex w-fit items-center gap-2 rounded-full border border-white/[0.07] bg-black/20 px-3 py-1.5 text-[10px] text-slate-400">
              <Users className="h-3.5 w-3.5 text-cyan-300" />
              {allocations.length} assignments
            </span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="border-b border-white/[0.06] bg-black/15 text-[9px] font-semibold uppercase tracking-[0.14em] text-slate-600">
                  <th className="px-4 py-3 text-center">Priority</th>
                  <th className="px-4 py-3">Hotspot Location</th>
                  <th className="px-4 py-3 text-center">Risk Tier</th>
                  <th className="px-5 py-3 text-right">Officers Assigned</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/[0.055] text-sm text-slate-300">
                {allocations.map((alloc) => (
                  <tr
                    key={alloc.hotspot_name}
                    className="transition duration-200 hover:bg-cyan-300/[0.035]"
                  >
                    <td className="px-4 py-3.5 text-center">
                      <span className="inline-flex h-7 min-w-12 items-center justify-center rounded-lg border border-white/[0.07] bg-white/[0.025] px-2 font-mono text-[10px] font-bold text-slate-400">
                        #{alloc.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3.5">
                      <div className="flex items-center gap-3">
                        <span className="h-2 w-2 rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(103,232,249,0.8)]" />
                        <span className="font-semibold text-slate-200">
                          {getLocationDisplayName(alloc.hotspot_name)}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <span
                        className={`rounded-full border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.1em] ${
                          alloc.risk_category === "Critical"
                            ? "border-rose-400/20 bg-rose-400/10 text-rose-200"
                            : alloc.risk_category === "High"
                              ? "border-amber-400/20 bg-amber-400/10 text-amber-200"
                              : "border-blue-400/20 bg-blue-400/10 text-blue-200"
                        }`}
                      >
                        {alloc.risk_category}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <span className="inline-flex min-w-12 justify-center rounded-lg border border-cyan-300/15 bg-cyan-300/[0.07] px-2 py-1 font-mono text-sm font-bold text-cyan-200">
                        {alloc.officers_allocated}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
