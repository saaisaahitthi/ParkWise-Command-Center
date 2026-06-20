import type {
  BackendSimulatorInput,
  BackendSimulationResult,
  BackendSimulatorPreset,
} from "@/types/backend";
import type {
  SimulatorBaselineView,
  SimulatorPresetView,
  SimulatorResultView,
} from "@/types/views";

export function adaptSimulatorBaseline(
  inputs: BackendSimulatorInput[]
): SimulatorBaselineView {
  const totalHotspots = inputs.length;
  const withOfficers = inputs.filter((i) => (i.officers_allocated ?? 0) > 0).length;
  const baseline_coverage =
    totalHotspots > 0 ? (withOfficers / totalHotspots) * 100 : 0;
  const baseline_eis_avg =
    totalHotspots > 0
      ? inputs.reduce((sum, i) => sum + i.current_eis, 0) / totalHotspots
      : 0;
  const baseline_total_officers = inputs.reduce(
    (sum, i) => sum + (i.officers_allocated ?? 0),
    0
  );

  return {
    baseline_coverage: Number(baseline_coverage.toFixed(1)),
    baseline_eis_avg: Number(baseline_eis_avg.toFixed(1)),
    total_hotspots: totalHotspots,
    baseline_total_officers,
  };
}

export function adaptSimulatorPreset(
  preset: BackendSimulatorPreset,
  index: number
): SimulatorPresetView {
  const overrides = preset.overrides ?? {};
  const officers =
    typeof overrides.total_officers === "number" ? overrides.total_officers : 20;
  const targetIds = overrides.target_hotspot_ids;
  const top_n_hotspots = Array.isArray(targetIds) ? targetIds.length : null;

  return {
    id: `preset-${index}`,
    name: preset.name,
    description: preset.description,
    officers,
    top_n_hotspots,
  };
}

export function adaptSimulationResult(
  result: BackendSimulationResult,
  baseline: SimulatorBaselineView
): SimulatorResultView {
  const simulated_coverage = Math.min(
    100,
    (result.simulated_total_officers / Math.max(result.baseline_total_officers, 1)) *
      baseline.baseline_coverage
  );

  return {
    simulated_coverage: Number(simulated_coverage.toFixed(1)),
    simulated_eis_avg: result.simulated_average_eis,
    recommendation: buildRecommendation(result),
    improved_hotspots: result.improved_hotspots,
    worsened_hotspots: result.worsened_hotspots,
  };
}

function buildRecommendation(result: BackendSimulationResult): string {
  const summary = result.summary ?? {};
  const improved = result.improved_hotspots;
  const worsened = result.worsened_hotspots;
  const eisDelta = result.average_eis_delta;

  if (improved > worsened && eisDelta < 0) {
    return `Scenario "${result.scenario_name}" improves ${improved} of ${result.total_hotspots} hotspots with average EIS down ${Math.abs(eisDelta).toFixed(1)} points.`;
  }
  if (worsened > improved && eisDelta > 0) {
    return `Scenario "${result.scenario_name}" worsens risk on ${worsened} hotspots. Consider increasing officer pool or enforcement intensity.`;
  }
  if (typeof summary.officers_added === "number" && summary.officers_added > 0) {
    return `Added ${summary.officers_added} officers across hotspots; average EIS ${result.simulated_average_eis.toFixed(1)}.`;
  }

  const note = result.hotspot_results?.[0]?.impact_notes?.[0];
  return note ?? `Simulation complete for ${result.total_hotspots} hotspots.`;
}
