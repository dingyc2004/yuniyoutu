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
    return payload.data || seedData[key] || [];
  } catch {
    return seedData[key] || [];
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

export async function fetchUser(userId) {
  try {
    const payload = await getJson(`/api/users/${encodeURIComponent(userId)}`);
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function fetchUserMembership(userId) {
  try {
    const payload = await getJson(`/api/users/${encodeURIComponent(userId)}/membership`);
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function fetchProfileSummary(userId) {
  try {
    const payload = await getJson(`/api/users/${encodeURIComponent(userId)}/profile-summary`);
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function createReport(userId, period = "lifetime") {
  try {
    const payload = await sendJson(`/api/users/${encodeURIComponent(userId)}/reports?period=${period}`, {
      method: "POST"
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function fetchReports(userId, period) {
  try {
    const query = period ? `?period=${encodeURIComponent(period)}` : "";
    const payload = await getJson(`/api/users/${encodeURIComponent(userId)}/reports${query}`);
    return payload.data || [];
  } catch {
    return [];
  }
}

export async function createPost(post) {
  try {
    const payload = await sendJson("/api/posts", {
      method: "POST",
      body: JSON.stringify(post)
    });
    return payload.data || null;
  } catch {
    return {
      ...post,
      id: `local_post_${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  }
}

export async function registerEvent(eventId, userId) {
  try {
    const payload = await sendJson(`/api/events/${encodeURIComponent(eventId)}/register`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId })
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function cancelEventRegistration(eventId, userId) {
  try {
    const payload = await sendJson(`/api/events/${encodeURIComponent(eventId)}/register?user_id=${encodeURIComponent(userId)}`, {
      method: "DELETE"
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function checkinEvent(eventId, userId) {
  try {
    const payload = await sendJson(`/api/events/${encodeURIComponent(eventId)}/checkin`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId })
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function createRecordFromEvent(eventId, userId) {
  try {
    const payload = await sendJson(`/api/events/${encodeURIComponent(eventId)}/create-record`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId })
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function fetchUserEvents(userId) {
  return fetchCollection(`/api/users/${encodeURIComponent(userId)}/events`, null);
}

export async function fetchLearningProgress(userId) {
  return fetchCollection(`/api/users/${encodeURIComponent(userId)}/learning-progress`, null);
}

export async function updateLearningProgress(tutorialId, userId, status, practiceNotes = "") {
  try {
    const payload = await sendJson(`/api/tutorials/${encodeURIComponent(tutorialId)}/progress`, {
      method: "PUT",
      body: JSON.stringify({ user_id: userId, status, practice_notes: practiceNotes })
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function fetchServiceRecommendations(userId) {
  try {
    const payload = await getJson(`/api/users/${encodeURIComponent(userId)}/service-recommendations`);
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function createOrder(userId, equipmentId, quantity = 1) {
  try {
    const payload = await sendJson("/api/orders", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, equipment_id: equipmentId, quantity })
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function fetchOrders(userId) {
  return fetchCollection(`/api/users/${encodeURIComponent(userId)}/orders`, null);
}

export async function payOrder(orderId, userId) {
  try {
    const payload = await sendJson(`/api/orders/${encodeURIComponent(orderId)}/pay`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId })
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function cancelOrder(orderId, userId) {
  try {
    const payload = await sendJson(`/api/orders/${encodeURIComponent(orderId)}?user_id=${encodeURIComponent(userId)}`, {
      method: "DELETE"
    });
    return payload.data || null;
  } catch {
    return null;
  }
}

export async function followUser(userId, followerId) {
  const payload = await sendJson(`/api/users/${encodeURIComponent(userId)}/follow`, {
    method: "POST",
    body: JSON.stringify({ follower_id: followerId })
  });
  return payload.data || null;
}

export async function unfollowUser(userId, followerId) {
  const payload = await sendJson(`/api/users/${encodeURIComponent(userId)}/follow?follower_id=${encodeURIComponent(followerId)}`, {
    method: "DELETE"
  });
  return payload.data || null;
}

export async function addFriend(userId, requesterId) {
  const payload = await sendJson(`/api/users/${encodeURIComponent(userId)}/friend`, {
    method: "POST",
    body: JSON.stringify({ requester_id: requesterId })
  });
  return payload.data || null;
}

export async function fetchDirectMessages(userId, peerId) {
  return fetchCollection(`/api/direct-messages/${encodeURIComponent(userId)}/${encodeURIComponent(peerId)}`, null);
}

export async function sendDirectMessage(peerId, senderId, content) {
  const payload = await sendJson(`/api/direct-messages/${encodeURIComponent(peerId)}`, {
    method: "POST",
    body: JSON.stringify({ sender_id: senderId, content })
  });
  return payload.data || null;
}

export async function sendGroupMessage(groupId, userId, content, author = "我") {
  const payload = await sendJson(`/api/groups/${encodeURIComponent(groupId)}/messages`, {
    method: "POST",
    body: JSON.stringify({ user_id: userId, author, content })
  });
  return payload.data || null;
}
