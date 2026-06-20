import { AlertTriangle } from "lucide-react";
import { Card } from "./card";

export function ErrorState({
  title = "Something went wrong",
  description = "We couldn’t load this view. Please refresh or try again later.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <Card className="rounded-[28px] border border-[var(--color-card-border)] p-8 text-center">
      <div className="mx-auto inline-flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10 text-red-400 shadow-[0_0_0_8px_rgba(239,68,68,0.15)]">
        <AlertTriangle className="h-8 w-8" />
      </div>
      <p className="mt-6 text-lg font-semibold text-white">{title}</p>
      <p className="mt-2 text-sm text-slate-400">{description}</p>
    </Card>
  );
}
