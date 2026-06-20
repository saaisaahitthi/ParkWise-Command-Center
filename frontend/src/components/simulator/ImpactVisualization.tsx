interface Props { metrics: { congestion: number; coverage: number; riskReduction: number } }

export function ImpactVisualization({ metrics }: Props) {
  const r1 = 18 + Math.round((metrics.riskReduction || 0) * 0.6);
  const r2 = 18 + Math.round((metrics.coverage || 0) * 0.18);

  return (
    <div className="rounded-[18px] border border-slate-700 bg-gradient-to-br from-slate-900/60 to-slate-950/40 p-4">
      <h4 className="text-sm font-semibold text-white">Visual command center</h4>
      <div className="mt-3 h-56 relative overflow-hidden">
        <svg viewBox="0 0 300 180" className="w-full h-full">
          <defs>
            <radialGradient id="g1"><stop offset="0%" stopColor="#ef4444" stopOpacity="0.95"/><stop offset="100%" stopColor="#ef4444" stopOpacity="0.05"/></radialGradient>
            <radialGradient id="g2"><stop offset="0%" stopColor="#f59e0b" stopOpacity="0.95"/><stop offset="100%" stopColor="#f59e0b" stopOpacity="0.05"/></radialGradient>
            <radialGradient id="g3"><stop offset="0%" stopColor="#34d399" stopOpacity="0.9"/><stop offset="100%" stopColor="#34d399" stopOpacity="0.04"/></radialGradient>
          </defs>

          {/* Pulsing critical hotspot */}
          <g>
            <circle cx={90} cy={70} r={r1} fill="url(#g1)">
              <animate attributeName="r" values={`${r1 - 4};${r1 + 8};${r1 - 4}`} dur="4s" repeatCount="indefinite" />
            </circle>
            <circle cx={90} cy={70} r={Math.max(6, r1 + 14)} fill="url(#g1)" opacity="0.06" />
          </g>

          {/* Medium hotspot */}
          <g>
            <circle cx={200} cy={110} r={r2} fill="url(#g2)">
              <animate attributeName="r" values={`${r2 - 3};${r2 + 6};${r2 - 3}`} dur="5s" repeatCount="indefinite" />
            </circle>
            <circle cx={200} cy={110} r={Math.max(8, r2 + 12)} fill="url(#g2)" opacity="0.05" />
          </g>

          {/* Supporting indicator */}
          <g>
            <circle cx={160} cy={40} r={12} fill="url(#g3)" opacity={0.9}>
              <animate attributeName="r" values="10;14;10" dur="6s" repeatCount="indefinite" />
            </circle>
          </g>

          <g fill="none" stroke="#cbd5e1" strokeOpacity="0.06">
            <path d="M20 160 C80 120 220 120 280 160" strokeWidth={1} />
            <path d="M40 140 C100 100 200 100 260 140" strokeWidth={1} />
          </g>
        </svg>
      </div>
    </div>
  );
}
