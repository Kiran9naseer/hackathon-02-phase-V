import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { getEnv } from "@/lib/config";
import { getToken as getAuthToken } from "@/lib/auth/hooks";

const apiClient = axios.create({
  baseURL: getEnv().NEXT_PUBLIC_API_URL,
  timeout: 30000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor - attach JWT token from HttpOnly cookie
apiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Skip token attachment for auth endpoints
    // Skip token attachment for login/register only, allow for session
    if (config.url?.includes("/auth/login") || config.url?.includes("/auth/register")) {
      return config;
    }

    try {
      const token = await getAuthToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error("Failed to get token for request:", error);
    }

    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle 401 errors globally
// Removing auto-redirect to prevent loops. Components should handle auth errors.
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // Just reject, let the caller handle it (or AuthProvider)
    return Promise.reject(error);
  }
);

export default apiClient;
