import {
  adaptSimulationResult,
  adaptSimulatorBaseline,
  adaptSimulatorPreset,
} from "@/adapters/simulator";
import { apiGet, apiPost } from "@/lib/api";
import type {
  BackendSimulationResult,
  BackendSimulatorInput,
  BackendSimulatorPreset,
} from "@/types/backend";
import type {
  SimulatorBaselineView,
  SimulatorPresetView,
  SimulatorResultView,
} from "@/types/views";

export async function fetchSimulatorBaseline(): Promise<SimulatorBaselineView> {
  const raw = await apiGet<BackendSimulatorInput[]>("/simulator/baseline");
  return adaptSimulatorBaseline(raw);
}

export async function fetchSimulatorPresets(): Promise<SimulatorPresetView[]> {
  const raw = await apiGet<BackendSimulatorPreset[]>("/simulator/presets");
  return raw.map(adaptSimulatorPreset);
}

export async function runSimulation(params: {
  officers: number;
  scenarioName?: string;
  baseline?: SimulatorBaselineView;
}): Promise<SimulatorResultView> {
  const baseline = params.baseline ?? (await fetchSimulatorBaseline());
  const raw = await apiPost<BackendSimulationResult>("/simulator/run", {
    scenario_name: params.scenarioName ?? `Officer pool ${params.officers}`,
    overrides: {
      total_officers: params.officers,
    },
  });
  return adaptSimulationResult(raw, baseline);
}
