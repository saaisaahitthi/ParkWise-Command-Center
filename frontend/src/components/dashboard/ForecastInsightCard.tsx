import { Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";

interface ForecastInsightCardProps {
  title: string;
  highlight: string;
  description: string;
}

export function ForecastInsightCard({ title, highlight, description }: ForecastInsightCardProps) {
  return (
    <Card className="rounded-[28px] border border-slate-700 bg-slate-950/80 p-5 shadow-[0_24px_64px_-40px_rgba(0,0,0,0.72)]">
      <div className="flex items-start gap-3">
        <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-orange-500/10 text-amber-300 shadow-lg shadow-orange-500/10">
          <Sparkles className="h-6 w-6" />
        </span>
        <div>
          <p className="text-sm uppercase tracking-[0.32em] text-slate-500">{title}</p>
          <p className="mt-2 text-base font-semibold text-white">{highlight}</p>
          <p className="mt-3 text-sm leading-6 text-slate-400">{description}</p>
        </div>
      </div>
    </Card>
  );
}
