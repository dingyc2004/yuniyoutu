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

async function sendJson(path, options = {}) {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(resolveApiPath(path), {
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {})
      },
      ...options
    });
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

export async function fetchFishingRecords(userId) {
  try {
    const query = userId ? `?user_id=${encodeURIComponent(userId)}` : "";
    const payload = await getJson(`/api/records${query}`);
    return payload.data || [];
  } catch {
    return [];
  }
}

export async function fetchFishingRecord(recordId) {
  try {
    const payload = await getJson(`/api/records/${encodeURIComponent(recordId)}`);
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function createFishingRecord(record) {
  try {
    const payload = await sendJson("/api/records", {
      method: "POST",
      body: JSON.stringify(record)
    });
    return payload.data || null;
  } catch {
    return {
      ...record,
      id: `local_record_${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      offline: true
    };
  }
}

export async function updateFishingRecord(recordId, patch) {
  try {
    const payload = await sendJson(`/api/records/${encodeURIComponent(recordId)}`, {
      method: "PATCH",
      body: JSON.stringify(patch)
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function deleteFishingRecord(recordId) {
  try {
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), timeout);
    const response = await fetch(resolveApiPath(`/api/records/${encodeURIComponent(recordId)}`), {
      method: "DELETE",
      signal: controller.signal
    });
    window.clearTimeout(timer);
    return response.ok;
  } catch {
    return false;
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

export async function fetchFishSpecies(name) {
  try {
    const payload = await getJson(`/api/fish-species/${encodeURIComponent(name)}`);
    return payload.data || null;
  } catch {
    return null;
  }
}
