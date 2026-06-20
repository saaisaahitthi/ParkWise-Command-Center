export const themeTokens = {
  background: "#0B1220",
  sidebar: "#111827",
  card: "#1F2937",
  border: "#334155",
  primary: "#3B82F6",
  success: "#10B981",
  warning: "#F59E0B",
  danger: "#EF4444",
  text: "#E5E7EB",
  muted: "#94A3B8",
};

export const typographyTokens = {
  display: "text-5xl sm:text-6xl font-display font-semibold tracking-tight",
  pageTitle: "text-4xl sm:text-5xl font-display font-semibold tracking-tight",
  sectionTitle: "text-3xl font-display font-semibold tracking-tight",
  cardTitle: "text-xl font-semibold tracking-tight",
  body: "text-base leading-7",
  caption: "text-sm text-slate-400 tracking-[0.02em]",
};

export const statusVariants = ["default", "success", "warning", "danger", "info"] as const;
export type StatusVariant = (typeof statusVariants)[number];

export const riskVariants = ["critical", "high", "medium", "low"] as const;
export type RiskVariant = (typeof riskVariants)[number];
