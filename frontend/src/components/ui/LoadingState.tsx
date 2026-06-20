import { Loader2 } from "lucide-react";
import { Card } from "./card";

export function LoadingState({ message = "Loading data, please wait..." }: { message?: string }) {
  return (
    <Card className="rounded-[28px] border border-[var(--color-card-border)] p-8 text-center">
      <div className="mx-auto inline-flex h-16 w-16 items-center justify-center rounded-full bg-slate-900 text-emerald-300 shadow-[0_0_0_8px_rgba(16,185,129,0.1)]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
      <p className="mt-6 text-sm text-slate-300">{message}</p>
    </Card>
  );
}
