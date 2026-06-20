import { create } from "zustand";
import { persist } from "zustand/middleware";

interface AppState {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (v: boolean) => void;
  useMockData: boolean;
  toggleMockData: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      sidebarCollapsed: true,
      useMockData: true, // Default to mock data mode for safety and instant demo
      toggleSidebar: () =>
        set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
      toggleMockData: () =>
        set((s) => ({ useMockData: !s.useMockData })),
    }),
    { name: "parkwise-app" }
  )
);
