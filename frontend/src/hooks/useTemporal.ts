import { useQuery } from "@tanstack/react-query";
import { fetchEisScores } from "@/services/temporal";

export function useEisScores() {
  return useQuery({
    queryKey: ["eis-scores"],
    queryFn: fetchEisScores,
    refetchInterval: 10_000,
  });
}
