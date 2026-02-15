import axios from "axios";

const isLocalHost =
  typeof window !== "undefined" &&
  ["localhost", "127.0.0.1"].includes(window.location.hostname);

const fallbackBaseURL = isLocalHost
  ? "http://127.0.0.1:8000/api"
  : "https://issuehub-jedu.onrender.com/api";

const baseURL = import.meta.env.VITE_API_BASE_URL || fallbackBaseURL;

const api = axios.create({
  baseURL,
});

// Attach token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
