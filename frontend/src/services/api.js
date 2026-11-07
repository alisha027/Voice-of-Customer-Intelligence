import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const API = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

export const getAnalyticsOverview = async () => {
  const response = await API.get("/api/analytics/overview");
  return response.data;
};

// Keep this export so existing imports don't break.
export const getOverview = getAnalyticsOverview;

export const analyzeVOC = async (query) => {
  const response = await API.post("/api/analysis", { query });
  return response.data;
};