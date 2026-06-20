// lightweight SVG map placeholder
import { type RouteRow } from "@/components/dashboard/RouteTable";

interface Props {
  routes: RouteRow[];
  onSelect?: (id: string) => void;
}

export function PatrolRouteMap({ routes, onSelect }: Props) {
  // Simple SVG placeholder rendering colored polylines and markers
  const colors = ["#60a5fa", "#f97316", "#ef4444", "#34d399"];

  return (
    <div className="h-full w-full rounded-lg bg-gradient-to-br from-slate-900/60 to-slate-950/40 p-4">
      <svg viewBox="0 0 1000 520" className="h-full w-full">
        {/* background grid */}
        <rect x={0} y={0} width={1000} height={520} fill="transparent" />

        {routes.slice(0,3).map((r, idx) => {
          const points = Array.from({ length: 5 }).map((__, pi) => `${80 + idx*40 + pi*150},${80 + (idx*40) + (pi%2===0? -20:20)}` ).join(" ");
          return (
            <g key={r.id} onClick={() => onSelect?.(r.id)} style={{ cursor: 'pointer' }}>
              <polyline points={points} fill="none" stroke={colors[idx % colors.length]} strokeWidth={4} strokeOpacity={0.95} strokeLinecap="round" strokeLinejoin="round" />
              {/* markers */}
              {Array.from({ length: 5 }).map((__, mi) => {
                const cx = 80 + idx*40 + mi*150;
                const cy = 80 + (idx*40) + (mi%2===0? -20:20);
                return <circle key={mi} cx={cx} cy={cy} r={6} fill={mi===0? colors[idx%colors.length] : "#0f172a"} stroke="#fff" strokeWidth={1} />;
              })}
            </g>
          );
        })}

        {/* hotspot markers */}
        <g>
          <circle cx={220} cy={160} r={8} fill="#ef4444" />
          <text x={240} y={165} fill="#cbd5e1" fontSize={12}>MG Road Junction</text>

          <circle cx={560} cy={240} r={8} fill="#f59e0b" />
          <text x={580} y={245} fill="#cbd5e1" fontSize={12}>Airport Access Road</text>

          <circle cx={420} cy={340} r={8} fill="#38bdf8" />
          <text x={440} y={345} fill="#cbd5e1" fontSize={12}>Metro Exit Gate 2</text>
        </g>
      </svg>
    </div>
  );
}
