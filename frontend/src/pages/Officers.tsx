import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { AlertTriangle, Shield, CheckCircle } from "lucide-react";
import { PageHeader } from "@/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { computeAllocation, fetchLatestAllocation } from "@/services/officers";

export default function OfficersPage() {
  const [totalOfficersInput, setTotalOfficersInput] = useState(20);
  const [topNHotspotsInput, setTopNHotspotsInput] = useState(4);
  const [updated, setUpdated] = useState(false);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["allocation-latest"],
    queryFn: fetchLatestAllocation,
    refetchInterval: 10_000,
  });

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
          Verify backend connectivity at{" "}
          <code className="text-red-200">http://127.0.0.1:8000/api/v1</code> or toggle header Mode
          to Mock.
        </p>
      </div>
    );
  }

  const { total_officers_allocated, hotspots_covered, deployment_window, allocations } = data;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Officer Allocation"
        description="Deploy field units proportionally based on current and forecasted intersection risk levels."
      />

      <div className="grid gap-4 sm:grid-cols-3">
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Total Officers Deployed
          </p>
          <p className="mt-4 text-3xl font-bold text-white">{total_officers_allocated}</p>
        </Card>
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Hotspots Covered
          </p>
          <p className="mt-4 text-3xl font-bold text-white">{hotspots_covered}</p>
        </Card>
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/70 p-5 shadow-lg">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500 font-semibold">
            Deployment Window
          </p>
          <p className="mt-4 text-lg font-semibold text-cyan-300 truncate">
            {deployment_window}
          </p>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-[300px_1fr]">
        <Card className="rounded-[28px] border border-slate-800 bg-slate-950/60 p-5 space-y-6 h-fit">
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-400">
              Calculator
            </h3>
            <p className="text-xs text-slate-500 mt-1">Adjust dispatcher parameters for model re-routing</p>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-xs font-semibold text-slate-400">
              <span>Total Available Officers</span>
              <span className="font-mono text-cyan-300 font-bold">{totalOfficersInput}</span>
            </div>
            <input
              type="range"
              min="5"
              max="100"
              step="5"
              value={totalOfficersInput}
              onChange={(e) => setTotalOfficersInput(Number(e.target.value))}
              className="w-full accent-cyan-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
            />
          </div>

          <div className="space-y-3">
            <div className="flex justify-between text-xs font-semibold text-slate-400">
              <span>Target Top Hotspots</span>
              <span className="font-mono text-cyan-300 font-bold">{topNHotspotsInput}</span>
            </div>
            <input
              type="range"
              min="2"
              max="10"
              step="1"
              value={topNHotspotsInput}
              onChange={(e) => setTopNHotspotsInput(Number(e.target.value))}
              className="w-full accent-cyan-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
            />
          </div>

          <button
            onClick={() => computeMutation.mutate()}
            disabled={computeMutation.isPending}
            className="w-full flex items-center justify-center gap-2 py-3 rounded-2xl border border-cyan-800 bg-cyan-950/60 hover:bg-cyan-950 text-cyan-300 font-semibold transition active:scale-95 disabled:opacity-50 cursor-pointer text-sm"
          >
            {computeMutation.isPending ? (
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
            ) : updated ? (
              <CheckCircle size={16} className="text-emerald-400" />
            ) : (
              <Shield size={16} />
            )}
            <span>{updated ? "Allocation Applied!" : "Optimize Allocations"}</span>
          </button>
        </Card>

        <Card className="rounded-[32px] border border-slate-800 bg-slate-950/45 p-6 overflow-hidden">
          <h3 className="text-md font-semibold text-white mb-4">Calculated Shift Allocations</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  <th className="py-3 px-4 text-center">Priority</th>
                  <th className="py-3 px-4">Hotspot Location</th>
                  <th className="py-3 px-4 text-center">Risk Tier</th>
                  <th className="py-3 px-4 text-right">Officers Assigned</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-sm text-slate-300">
                {allocations.map((alloc) => (
                  <tr
                    key={`${alloc.hotspot_id}-${alloc.priority}`}
                    className="hover:bg-slate-900/20 transition-colors"
                  >
                    <td className="py-4 px-4 text-center font-mono font-bold text-slate-400">
                      Rank {alloc.priority}
                    </td>
                    <td className="py-4 px-4 font-medium text-slate-200">{alloc.hotspot_name}</td>
                    <td className="py-4 px-4 text-center">
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-semibold border ${
                          alloc.risk_category === "Critical"
                            ? "border-red-900 bg-red-950/40 text-red-300"
                            : alloc.risk_category === "High"
                              ? "border-amber-900 bg-amber-950/40 text-amber-300"
                              : "border-blue-900 bg-blue-950/40 text-blue-300"
                        }`}
                      >
                        {alloc.risk_category}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-right font-mono text-cyan-300 font-bold pr-8">
                      {alloc.officers_allocated}
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
