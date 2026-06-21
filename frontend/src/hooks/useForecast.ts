import { useQuery } from "@tanstack/react-query";
import { getForecastSummary, getTopForecasts } from "@/services/forecast";

export function useForecastSummary() {
  return useQuery({
    queryKey: ["forecast-summary"],
    queryFn: getForecastSummary,
    refetchInterval: 10_000,
  });
}

export function useTopForecasts() {
  return useQuery({
    queryKey: ["forecast-top"],
    queryFn: getTopForecasts,
    refetchInterval: 10_000,
  });
}
