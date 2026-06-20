import apiClient from "./axios";
import { useAppStore } from "@/stores/appStore";
import { getMockResponse, getMockPostResponse } from "@/services/mockData";
import type { ApiResponse } from "@/types";

function unwrapResponse<T>(data: T | ApiResponse<T>): T {
  if (
    data &&
    typeof data === "object" &&
    "data" in data &&
    "status" in data &&
    (data as ApiResponse<T>).status === "success"
  ) {
    return (data as ApiResponse<T>).data;
  }
  return data as T;
}

export async function apiGet<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const useMock = useAppStore.getState().useMockData;
  if (useMock) {
    await new Promise((resolve) => setTimeout(resolve, 350));
    return getMockResponse<T>(url, params);
  }
  const { data } = await apiClient.get<T | ApiResponse<T>>(url, { params });
  return unwrapResponse(data);
}

export async function apiPost<T>(url: string, body?: unknown): Promise<T> {
  const useMock = useAppStore.getState().useMockData;
  if (useMock) {
    await new Promise((resolve) => setTimeout(resolve, 350));
    return getMockPostResponse<T>(url, body);
  }
  const { data } = await apiClient.post<T | ApiResponse<T>>(url, body);
  return unwrapResponse(data);
}
