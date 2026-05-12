import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "./auth";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  headers: { "Content-Type": "application/json" },
});

let isRefreshing = false;
let failedQueue: {
  resolve: (value?: unknown) => void;
  reject: (err: any) => void;
  config: AxiosRequestConfig;
}[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject, config }) => {
    if (error) reject(error);
    else {
      if (token && config.headers) config.headers["Authorization"] = `Bearer ${token}`;
      resolve(api(config));
    }
  });
  failedQueue = [];
};

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token && config.headers) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (err: AxiosError) => {
    const originalConfig = err.config!;
    if (err.response?.status === 401 && !originalConfig._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject, config: originalConfig });
        });
      }

      originalConfig._retry = true;
      isRefreshing = true;

      const refresh = getRefreshToken();
      if (!refresh) {
        clearTokens();
        isRefreshing = false;
        return Promise.reject(err);
      }

      try {
        const resp = await axios.post(
          "/auth/refresh",
          { refresh_token: refresh },
          { baseURL: api.defaults.baseURL, headers: { "Content-Type": "application/json" } }
        );
        const data = resp.data;

        setTokens({
          accessToken: data.access_token,
          refreshToken: data.refresh_token,
          expiresIn: data.expires_in,
        });
        processQueue(null, data.access_token);
        isRefreshing = false;
    
        if (originalConfig.headers) originalConfig.headers["Authorization"] = `Bearer ${data.access_token}`;
        return api(originalConfig);
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        clearTokens();
        isRefreshing = false;
        return Promise.reject(refreshErr);
      }
    }
    return Promise.reject(err);
  }
);

export default api;
