interface Props { recommendations: string[] }

export function RecommendationPanel({ recommendations }: Props) {
  return (
    <div className="rounded-[18px] border border-slate-700 bg-slate-950/80 p-4">
      <h4 className="text-sm font-semibold text-white">AI recommendations</h4>
      <ul className="mt-3 space-y-2">
        {recommendations.map((r, i) => (
          <li key={i} className="rounded-md border border-slate-800 bg-slate-900/60 p-3 text-sm text-slate-200">{r}</li>
        ))}
      </ul>
    </div>
  );
}
