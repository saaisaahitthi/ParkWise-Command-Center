import { Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";

interface InsightCardProps {
  title: string;
  description: string;
  highlight: string;
}

export function InsightCard({ title, description, highlight }: InsightCardProps) {
  return (
    <Card className="rounded-[28px] border border-slate-700 bg-slate-950/80 p-5 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <div className="flex items-center gap-3">
        <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-cyan-500/10 text-cyan-300 shadow-lg shadow-cyan-500/10">
          <Sparkles className="h-6 w-6" />
        </span>
        <div>
          <p className="text-sm uppercase tracking-[0.32em] text-slate-500">{title}</p>
          <p className="mt-2 text-base font-semibold text-white">{highlight}</p>
        </div>
      </div>
      <p className="mt-4 text-sm leading-6 text-slate-400">{description}</p>
    </Card>
  );
}
