import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://parkwise-command-center.onrender.com/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30_000,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Request interceptor — attach auth token if present
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("parkwise_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor — normalise errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const message =
      error.response?.data?.detail ??
      error.response?.data?.message ??
      error.message ??
      "An unexpected error occurred";

    if (status === 401) {
      localStorage.removeItem("parkwise_token");
      window.location.href = "/login";
    }

    return Promise.reject({ status, message, raw: error });
  }
);

export default apiClient;
