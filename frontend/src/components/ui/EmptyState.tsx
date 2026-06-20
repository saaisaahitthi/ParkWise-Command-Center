import { FileSearch } from "lucide-react";
import { Card } from "./card";

export function EmptyState({
  title = "No results found",
  description = "Try updating your filters or coming back later.",
}: {
  title?: string;
  description?: string;
}) {
  return (
    <Card className="rounded-[28px] border border-[var(--color-card-border)] p-8 text-center">
      <div className="mx-auto inline-flex h-16 w-16 items-center justify-center rounded-full bg-slate-900 text-slate-200 shadow-[0_0_0_8px_rgba(148,163,184,0.12)]">
        <FileSearch className="h-8 w-8" />
      </div>
      <p className="mt-6 text-lg font-semibold text-white">{title}</p>
      <p className="mt-2 text-sm text-slate-400">{description}</p>
    </Card>
  );
}
