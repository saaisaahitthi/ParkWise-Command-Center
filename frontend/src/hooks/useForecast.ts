import { useQuery } from "@tanstack/react-query";
import { fetchForecastSummary, fetchTopForecasts } from "@/services/forecast";

export function useForecastSummary() {
  return useQuery({
    queryKey: ["forecast-summary"],
    queryFn: fetchForecastSummary,
    refetchInterval: 10_000,
  });
}

export function useTopForecasts() {
  return useQuery({
    queryKey: ["forecast-top"],
    queryFn: fetchTopForecasts,
    refetchInterval: 10_000,
  });
}
