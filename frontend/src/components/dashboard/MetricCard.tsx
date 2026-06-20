import { type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { Card } from "@/components/ui/card";

interface MetricCardProps {
  label: string;
  value: string;
  delta: string;
  icon: LucideIcon;
  accent: string;
}

export function MetricCard({ label, value, delta, icon: Icon, accent }: MetricCardProps) {
  return (
    <Card className="p-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-3 text-slate-400">
            <div className={cn("flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-700", accent)}>
              <Icon className="h-5 w-5" />
            </div>
            <span className="text-xs uppercase tracking-[0.32em] text-slate-500">{label}</span>
          </div>

          <p className="text-3xl font-semibold text-white">{value}</p>
        </div>

        <span className="rounded-2xl bg-slate-900/80 px-3 py-2 text-sm font-semibold text-slate-200">
          {delta}
        </span>
      </div>

      <div className="mt-5 h-1 rounded-full bg-slate-800" />
      <p className="mt-3 text-sm text-slate-400">Monitoring real-time enforcement metrics across the city.</p>
    </Card>
  );
}
