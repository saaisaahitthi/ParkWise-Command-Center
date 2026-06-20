import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  ChevronDown,
  CircleParking,
  CloudSun,
  MapPin,
  Navigation,
  Route,
  Shield,
  Sparkles,
  Users,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";
import {
  landingDemoData,
  resolveLandingOverviewData,
  type LandingHotspotMarker,
  type LandingLayerIcon,
} from "@/data/landingDemoData";

const layerIcons: Record<LandingLayerIcon, LucideIcon> = {
  critical: AlertTriangle,
  risk: BarChart3,
  route: Route,
  officers: Users,
  forecast: CloudSun,
};

function MapMarker({
  label,
  left,
  top,
  level,
}: LandingHotspotMarker) {
  const critical = level === "critical";
  const high = level === "high";
  const markerColor = critical
    ? "bg-rose-400 shadow-[0_0_20px_rgba(251,113,133,0.95)]"
    : high
      ? "bg-amber-300 shadow-[0_0_20px_rgba(252,211,77,0.85)]"
      : "bg-cyan-300 shadow-[0_0_20px_rgba(103,232,249,0.8)]";

  return (
    <div className="absolute z-10" style={{ left, top }}>
      <div className="group relative -translate-x-1/2 -translate-y-1/2">
        <span
          className={`absolute left-1/2 top-1/2 h-9 w-9 -translate-x-1/2 -translate-y-1/2 rounded-full border ${
            critical
              ? "border-rose-400/25"
              : high
                ? "border-amber-300/20"
                : "border-cyan-300/20"
          }`}
        />
        <span className={`relative block h-3 w-3 rounded-full ${markerColor}`} />
        <span className="pointer-events-none absolute left-1/2 top-5 -translate-x-1/2 whitespace-nowrap rounded-lg border border-white/[0.08] bg-slate-950/85 px-2 py-1 text-[9px] font-semibold text-slate-200 opacity-80 shadow-lg backdrop-blur-md transition group-hover:-translate-y-0.5 group-hover:opacity-100 sm:text-[10px]">
          {label}
        </span>
      </div>
    </div>
  );
}

function LandingNavbar({
  navigation,
}: {
  navigation: typeof landingDemoData.navigation;
}) {
  return (
    <header className="absolute inset-x-0 top-0 z-40 border-b border-white/[0.08] bg-[#071019]/88 shadow-[0_18px_55px_-42px_rgba(34,211,238,0.5)] backdrop-blur-2xl">
      <div className="mx-auto flex h-[72px] max-w-[1600px] items-center gap-6 px-4 sm:px-6 lg:px-9">
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
          className="flex min-w-0 flex-1 items-center justify-start gap-1.5 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden lg:justify-center"
          aria-label="Primary navigation"
        >
          {navigation.map((item, index) => (
            <Link
              key={item.path}
              to={item.path}
              className={`group relative shrink-0 rounded-xl px-3.5 py-2.5 text-xs font-semibold tracking-[0.01em] transition duration-300 xl:px-4 xl:text-[13px] ${
                index === 0
                  ? "bg-cyan-300/[0.075] text-cyan-100"
                  : "text-slate-400 hover:bg-white/[0.045] hover:text-white"
              }`}
            >
              {item.label}
              <span
                className={`absolute inset-x-3 -bottom-[9px] h-0.5 origin-center rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(103,232,249,0.85)] transition-transform duration-300 ${
                  index === 0 ? "scale-x-100" : "scale-x-0 group-hover:scale-x-100"
                }`}
              />
            </Link>
          ))}
        </nav>

        <button
          className="hidden shrink-0 items-center gap-2.5 rounded-[14px] border border-white/[0.09] bg-white/[0.04] p-1.5 pr-3 text-left shadow-lg shadow-black/15 transition duration-300 hover:border-cyan-300/20 hover:bg-white/[0.065] md:flex"
          aria-label="Operator profile"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-[10px] border border-cyan-300/10 bg-cyan-300/[0.09] text-[10px] font-bold text-cyan-100">
            OP
          </span>
          <span className="hidden xl:block">
            <span className="block text-xs font-semibold text-white">
              Operator
            </span>
            <span className="block text-[9px] text-slate-500">
              Command room
            </span>
          </span>
          <ChevronDown className="h-3.5 w-3.5 text-slate-500" />
        </button>
      </div>
    </header>
  );
}

export default function LandingPage() {
  // Pass a mapped API result here once a confirmed landing-overview contract
  // exists. Until then, the resolver safely returns the configured fallback.
  const landingData = resolveLandingOverviewData();
  const {
    navigation,
    hero,
    workflow,
    mapLayers,
    hotspots,
    selectedHotspot,
    stats,
  } = landingData;

  return (
    <div className="relative min-h-[100svh] overflow-x-hidden bg-[#070d14] text-slate-100 lg:h-[100svh] lg:overflow-hidden">
      <LandingNavbar navigation={navigation} />

      <main className="relative min-h-[100svh] overflow-x-hidden pt-[72px] lg:h-[100svh] lg:overflow-hidden">
        <div className="absolute inset-0 top-[72px] bg-[radial-gradient(circle_at_62%_40%,rgba(17,82,96,0.34),transparent_38%),linear-gradient(135deg,#071019_0%,#0c1923_52%,#07121b_100%)]" />
        <div className="absolute inset-0 top-[72px] opacity-90 [background-image:linear-gradient(rgba(118,148,164,0.075)_1px,transparent_1px),linear-gradient(90deg,rgba(118,148,164,0.075)_1px,transparent_1px)] [background-size:46px_46px] [mask-image:radial-gradient(ellipse_at_center,black_42%,transparent_94%)]" />

        <svg
          aria-hidden="true"
          className="absolute inset-0 top-[72px] h-[calc(100%-72px)] w-full opacity-95"
          viewBox="0 0 1600 900"
          preserveAspectRatio="none"
        >
          <g fill="none" strokeLinecap="round">
            <path
              d="M-60 790 C160 670 260 760 410 620 S690 270 850 390 S1070 650 1260 470 S1460 250 1690 320"
              stroke="rgba(46,112,126,0.25)"
              strokeWidth="34"
            />
            <path
              d="M-60 790 C160 670 260 760 410 620 S690 270 850 390 S1070 650 1260 470 S1460 250 1690 320"
              stroke="rgba(94,234,212,0.84)"
              strokeWidth="3.5"
              strokeDasharray="13 14"
            />
            <path
              d="M80 100 C280 240 390 150 550 280 S780 650 1030 540 S1330 170 1600 230"
              stroke="rgba(148,163,184,0.24)"
              strokeWidth="15"
            />
            <path
              d="M80 100 C280 240 390 150 550 280 S780 650 1030 540 S1330 170 1600 230"
              stroke="rgba(251,191,36,0.68)"
              strokeWidth="3"
              strokeDasharray="8 18"
            />
            <path
              d="M330 -40 C360 160 520 270 470 470 S360 740 520 940"
              stroke="rgba(82,123,139,0.22)"
              strokeWidth="22"
            />
            <path
              d="M1040 -40 C980 160 1130 260 1060 430 S910 740 980 940"
              stroke="rgba(82,123,139,0.2)"
              strokeWidth="18"
            />
            <path
              d="M1380 -40 C1290 150 1420 340 1330 540 S1220 760 1300 940"
              stroke="rgba(82,123,139,0.18)"
              strokeWidth="13"
            />
          </g>
        </svg>

        <div className="pointer-events-none absolute inset-0 top-[72px] bg-[linear-gradient(90deg,rgba(4,9,14,0.88)_0%,rgba(4,9,14,0.68)_30%,rgba(4,9,14,0.05)_59%,rgba(4,9,14,0.1)_100%)]" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-[#070d14]/88 via-[#070d14]/35 to-transparent" />

        {hotspots.map((marker) => (
          <MapMarker key={marker.label} {...marker} />
        ))}

        <aside className="absolute left-5 top-28 z-20 hidden w-56 overflow-hidden rounded-[22px] border border-white/[0.09] bg-[linear-gradient(155deg,rgba(12,25,36,0.94),rgba(7,16,25,0.86))] p-3.5 shadow-[0_30px_80px_-42px_rgba(0,0,0,0.9)] backdrop-blur-2xl xl:block">
          <div className="border-b border-white/[0.075] px-2 pb-3.5 pt-0.5">
            <p className="text-[9px] font-semibold uppercase tracking-[0.26em] text-cyan-300/65">
              Map layers
            </p>
            <p className="mt-1.5 text-[15px] font-semibold tracking-tight text-white">
              City operations
            </p>
            <p className="mt-1 text-[10px] leading-4 text-slate-500">
              Priority signals across Bengaluru
            </p>
          </div>
          <div className="mt-3 space-y-1.5">
            {mapLayers.map((category, index) => {
              const Icon = layerIcons[category.icon];
              return (
                <div
                  key={category.label}
                  className={`group flex items-center gap-3 rounded-[14px] border px-2.5 py-2.5 transition duration-300 ${
                    index === 0
                      ? "border-cyan-300/15 bg-cyan-300/[0.075] shadow-[0_12px_28px_-22px_rgba(103,232,249,0.8)]"
                      : "border-transparent hover:border-white/[0.08] hover:bg-white/[0.045]"
                  }`}
                >
                  <span
                    className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-white/[0.06] bg-white/[0.045] shadow-inner shadow-white/[0.02] transition group-hover:scale-105 ${category.color}`}
                  >
                    <Icon className="h-4 w-4" />
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-[12px] font-semibold text-slate-200">
                      {category.label}
                    </span>
                    <span className="mt-0.5 block text-[9px] font-medium text-slate-500">
                      {category.detail}
                    </span>
                  </span>
                </div>
              );
            })}
          </div>
        </aside>

        <section className="relative z-20 mx-auto flex min-h-[calc(100svh-72px)] max-w-[1600px] items-center px-5 pb-10 pt-8 sm:px-8 sm:pb-32 lg:h-[calc(100svh-72px)] lg:min-h-0 lg:px-12 lg:pb-24 lg:pt-5 xl:pl-[18.5rem]">
          <div className="relative max-w-[680px] rounded-[30px] border border-white/[0.07] bg-[linear-gradient(100deg,rgba(4,10,16,0.86)_0%,rgba(5,13,20,0.7)_68%,rgba(5,13,20,0.08)_100%)] px-6 py-6 shadow-[0_34px_90px_-58px_rgba(0,0,0,1)] backdrop-blur-[4px] sm:px-8 sm:py-7 lg:-ml-2 lg:px-9 lg:py-7">
            <div className="pointer-events-none absolute -inset-8 -z-10 bg-[radial-gradient(ellipse_at_left,rgba(2,8,13,0.92)_0%,rgba(2,8,13,0.56)_45%,transparent_76%)] blur-lg" />

            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-300/18 bg-cyan-300/[0.07] px-3.5 py-1.5 text-[9px] font-semibold uppercase tracking-[0.24em] text-cyan-100/85 shadow-[0_0_24px_-14px_rgba(103,232,249,0.7)] backdrop-blur-md">
              <Sparkles className="h-3 w-3" />
              {hero.eyebrow}
            </div>

            <h1 className="mt-5 max-w-[640px] font-display text-[40px] font-bold leading-[0.98] tracking-[-0.035em] text-white drop-shadow-[0_4px_24px_rgba(0,0,0,0.78)] sm:text-[49px] lg:text-[56px] xl:text-[60px]">
              <span className="text-white">{hero.title}</span>
              <span className="mt-2 block bg-gradient-to-r from-cyan-200 via-cyan-100 to-sky-200 bg-clip-text text-transparent">
                {hero.highlightedTitle}
              </span>
            </h1>

            <p className="mt-5 max-w-[590px] text-[14px] leading-6 text-slate-300 sm:text-[15px]">
              {hero.subtitle}
            </p>

            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <Link
                to="/dashboard"
                className="group inline-flex min-h-12 items-center justify-center gap-2 rounded-[14px] bg-cyan-300 px-5 py-3 text-sm font-bold text-slate-950 shadow-[0_18px_45px_-20px_rgba(103,232,249,0.95)] transition duration-300 hover:-translate-y-0.5 hover:bg-cyan-200"
              >
                Launch Dashboard
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
              </Link>
              <Link
                to="/hotspots"
                className="inline-flex min-h-12 items-center justify-center gap-2 rounded-[14px] border border-white/12 bg-slate-950/55 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-black/20 backdrop-blur-md transition duration-300 hover:-translate-y-0.5 hover:border-cyan-300/25 hover:bg-white/[0.075]"
              >
                Explore Hotspots
                <MapPin className="h-4 w-4 text-cyan-300" />
              </Link>
            </div>

            <div className="mt-6 flex w-fit max-w-full flex-wrap items-center gap-1.5 rounded-2xl border border-white/[0.075] bg-black/20 p-1.5 shadow-inner shadow-black/20 backdrop-blur-md sm:gap-2">
              {workflow.map((step, index) => (
                <div key={step} className="flex items-center gap-2 sm:gap-2.5">
                  <span
                    className={`group flex items-center gap-2 rounded-xl px-2.5 py-1.5 text-[11px] font-semibold tracking-wide transition duration-300 sm:text-xs ${
                      index === 0
                        ? "bg-rose-400/[0.08] text-rose-200"
                        : index === workflow.length - 1
                          ? "bg-cyan-300/[0.08] text-cyan-200"
                          : "text-slate-300 hover:bg-white/[0.045] hover:text-white"
                    }`}
                  >
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${
                        index === 0
                          ? "bg-rose-400 shadow-[0_0_8px_rgba(251,113,133,0.8)]"
                          : index === workflow.length - 1
                            ? "bg-cyan-300 shadow-[0_0_8px_rgba(103,232,249,0.8)]"
                            : "bg-slate-500"
                      }`}
                    />
                    {step}
                  </span>
                  {index < workflow.length - 1 && (
                    <ArrowRight className="h-3.5 w-3.5 shrink-0 text-slate-600" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        <div className="absolute bottom-[92px] right-5 z-20 hidden w-[300px] overflow-hidden rounded-[22px] border border-white/[0.1] bg-[linear-gradient(155deg,rgba(12,25,36,0.94),rgba(7,15,24,0.88))] p-4 shadow-[0_35px_90px_-45px_rgba(0,0,0,1)] backdrop-blur-xl lg:block xl:right-10">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-rose-300/50 to-transparent" />
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[9px] font-semibold uppercase tracking-[0.24em] text-rose-300/80">
                {selectedHotspot.eyebrow}
              </p>
              <h2 className="mt-2 text-lg font-semibold tracking-tight text-white">
                {selectedHotspot.title}
              </h2>
            </div>
            <span className="flex h-10 w-10 items-center justify-center rounded-[13px] border border-rose-400/20 bg-rose-400/[0.09] text-rose-300 shadow-[0_0_22px_-10px_rgba(251,113,133,0.8)]">
              <Navigation className="h-[18px] w-[18px]" />
            </span>
          </div>

          <div className="mt-4 grid grid-cols-[auto_1fr] gap-x-4 gap-y-2.5 border-t border-white/[0.075] pt-3.5 text-xs">
            <span className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
              Location
            </span>
            <span className="text-right font-semibold text-slate-200">
              {selectedHotspot.location}
            </span>
            <span className="self-center text-[10px] font-medium uppercase tracking-wider text-slate-500">
              Risk
            </span>
            <span className="justify-self-end rounded-full border border-rose-400/20 bg-rose-400/[0.09] px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider text-rose-200">
              {selectedHotspot.risk}
            </span>
            <span className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
              Suggested Action
            </span>
            <span className="text-right font-semibold text-slate-200">
              {selectedHotspot.suggestedAction}
            </span>
            <span className="text-[10px] font-medium uppercase tracking-wider text-slate-500">
              Route
            </span>
            <span className="text-right font-semibold text-cyan-300">
              {selectedHotspot.route}
            </span>
          </div>
        </div>

        <div className="relative z-30 mt-2 border-y border-white/[0.08] bg-[#071019]/95 shadow-[0_-22px_65px_-48px_rgba(103,232,249,0.55)] backdrop-blur-2xl sm:absolute sm:inset-x-0 sm:bottom-0 sm:mt-0">
          <div className="mx-auto grid max-w-[1600px] grid-cols-2 divide-x divide-white/[0.07] px-4 sm:grid-cols-4 sm:px-8">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="group relative px-3 py-3 text-center transition hover:bg-white/[0.035] sm:px-5 sm:py-3.5"
              >
                <span className="absolute inset-x-5 top-0 h-px bg-gradient-to-r from-transparent via-cyan-300/25 to-transparent opacity-0 transition group-hover:opacity-100" />
                <p className="font-mono text-base font-semibold tracking-tight text-white transition group-hover:text-cyan-100 sm:text-[17px]">
                  {stat.value}
                </p>
                <p className="mt-0.5 text-[8px] font-semibold uppercase tracking-[0.16em] text-slate-400 sm:text-[9px]">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="absolute right-5 top-24 z-20 hidden flex-col gap-2 sm:flex">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/[0.08] bg-[#09131d]/80 text-slate-400 backdrop-blur-lg">
            <Shield className="h-4 w-4" />
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-white/[0.08] bg-[#09131d]/80 text-cyan-300 backdrop-blur-lg">
            <Navigation className="h-4 w-4" />
          </div>
        </div>
      </main>
    </div>
  );
}
