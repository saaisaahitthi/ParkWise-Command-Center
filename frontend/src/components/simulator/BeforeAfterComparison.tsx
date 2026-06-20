interface Props {
  before: Record<string, string | number>;
  after: Record<string, string | number>;
}

export function BeforeAfterComparison({ before, after }: Props) {
  const keys = Object.keys(before);
  return (
    <div className="rounded-[18px] border border-slate-700 bg-slate-950/80 p-4">
      <h4 className="text-sm font-semibold text-white">Before vs After</h4>
      <div className="mt-3 grid gap-2">
        {keys.map((k) => (
          <div key={k} className="flex items-center justify-between">
            <div className="text-sm text-slate-400">{k}</div>
            <div className="text-sm text-slate-200">{before[k]} → <span className="font-semibold text-white">{after[k]}</span></div>
          </div>
        ))}
      </div>
    </div>
  );
}
