import { seedData } from "../data/seedData";

const timeout = 1800;
const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

function resolveApiPath(path) {
  if (!apiBaseUrl) return path;
  return `${apiBaseUrl}${path.startsWith("/") ? path : `/${path}`}`;
}

async function getJson(path) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(resolveApiPath(path), { signal: controller.signal });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } finally {
    window.clearTimeout(timer);
  }
}

export async function fetchCollection(path, key) {
  try {
    const payload = await getJson(path);
    return payload.data || seedData[key];
  } catch {
    return seedData[key];
  }
}

export async function fetchAmapConfig() {
  try {
    const payload = await getJson("/api/amap/config");
    return payload.data || {};
  } catch {
    return {};
  }
}
