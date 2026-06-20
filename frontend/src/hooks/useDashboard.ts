import { useQuery } from "@tanstack/react-query";
import { fetchDashboard } from "@/services/dashboard";

export function useDashboard() {
  return useQuery({
    queryKey: ["dashboard-full"],
    queryFn: fetchDashboard,
    refetchInterval: 10_000,
  });
}
