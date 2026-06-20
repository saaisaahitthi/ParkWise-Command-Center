import { Bell, ChevronDown, CircleParking } from "lucide-react";
import { Link, NavLink } from "react-router-dom";

const navigation = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Hotspots", path: "/hotspots" },
  { label: "Risk Score", path: "/temporal" },
  { label: "Forecast", path: "/forecast" },
  { label: "Allocation", path: "/officers" },
  { label: "Patrol", path: "/patrol" },
];

export function HorizontalNavbar() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-white/[0.08] bg-[#071019]/92 shadow-[0_18px_55px_-42px_rgba(34,211,238,0.5)] backdrop-blur-2xl">
      <div className="mx-auto flex h-[72px] max-w-[1800px] items-center gap-5 px-4 sm:px-6 lg:px-8">
        <Link
          to="/landing"
          className="group flex shrink-0 items-center gap-3"
          aria-label="ParkWise home"
        >
          <span className="flex h-10 w-10 items-center justify-center rounded-[14px] border border-cyan-300/20 bg-[linear-gradient(145deg,rgba(103,232,249,0.14),rgba(34,211,238,0.04))] text-cyan-200 shadow-[0_0_28px_-10px_rgba(79,209,197,0.9)] transition duration-300 group-hover:border-cyan-200/30 group-hover:bg-cyan-300/[0.12]">
            <CircleParking className="h-[21px] w-[21px]" />
          </span>
          <span className="hidden sm:block">
            <span className="block font-display text-[19px] font-bold leading-none tracking-[0.03em] text-white">
              ParkWise
            </span>
            <span className="mt-1.5 block text-[8px] font-semibold uppercase tracking-[0.24em] text-cyan-300/60">
              Bengaluru Intelligence
            </span>
          </span>
        </Link>

        <nav
          className="flex min-w-0 flex-1 items-center justify-start gap-1 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden lg:justify-center"
          aria-label="Primary navigation"
        >
          {navigation.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `group relative shrink-0 rounded-xl px-3 py-2.5 text-xs font-semibold tracking-[0.01em] transition duration-300 xl:px-4 xl:text-[13px] ${
                  isActive
                    ? "bg-cyan-300/[0.08] text-cyan-100"
                    : "text-slate-400 hover:bg-white/[0.045] hover:text-white"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {item.label}
                  <span
                    className={`absolute inset-x-3 -bottom-[9px] h-0.5 origin-center rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(103,232,249,0.85)] transition-transform duration-300 ${
                      isActive
                        ? "scale-x-100"
                        : "scale-x-0 group-hover:scale-x-100"
                    }`}
                  />
                </>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            className="relative hidden h-9 w-9 items-center justify-center rounded-xl border border-transparent text-slate-400 transition hover:border-white/[0.08] hover:bg-white/[0.05] hover:text-white sm:flex"
            aria-label="View notifications"
          >
            <Bell className="h-[17px] w-[17px]" />
            <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-rose-400 shadow-[0_0_7px_rgba(251,113,133,0.9)]" />
          </button>

          <button
            type="button"
            className="hidden items-center gap-2.5 rounded-[14px] border border-white/[0.09] bg-[linear-gradient(145deg,rgba(255,255,255,0.055),rgba(255,255,255,0.025))] p-1.5 pr-3 text-left shadow-[0_12px_32px_-24px_rgba(34,211,238,0.55)] transition duration-300 hover:border-cyan-300/20 hover:bg-white/[0.07] md:flex"
            aria-label="Operator profile"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-[10px] border border-cyan-300/15 bg-cyan-300/[0.1] text-[10px] font-bold text-cyan-100 shadow-[0_0_18px_-9px_rgba(103,232,249,0.8)]">
              OP
            </span>
            <span className="hidden lg:block">
              <span className="block text-xs font-semibold text-white">
                Operator
              </span>
              <span className="block text-[9px] text-slate-500">
                Control Room
              </span>
            </span>
            <ChevronDown className="h-3.5 w-3.5 text-slate-500" />
          </button>
        </div>
      </div>
    </header>
  );
}
