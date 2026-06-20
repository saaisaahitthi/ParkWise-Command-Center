import { create } from "zustand";

export type DateRange = { from: string; to: string };

interface FilterState {
  selectedZones: string[];
  selectedViolationTypes: string[];
  dateRange: DateRange;
  setZones: (zones: string[]) => void;
  setViolationTypes: (types: string[]) => void;
  setDateRange: (range: DateRange) => void;
  resetAll: () => void;
}

const DEFAULT_DATE_RANGE: DateRange = {
  from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split("T")[0],
  to: new Date().toISOString().split("T")[0],
};

export const useFilterStore = create<FilterState>()((set) => ({
  selectedZones: [],
  selectedViolationTypes: [],
  dateRange: DEFAULT_DATE_RANGE,
  setZones: (zones) => set({ selectedZones: zones }),
  setViolationTypes: (types) => set({ selectedViolationTypes: types }),
  setDateRange: (range) => set({ dateRange: range }),
  resetAll: () =>
    set({
      selectedZones: [],
      selectedViolationTypes: [],
      dateRange: DEFAULT_DATE_RANGE,
    }),
}));
