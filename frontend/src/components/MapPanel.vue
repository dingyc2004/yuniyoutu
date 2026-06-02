<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { fetchAmapConfig } from "../services/api";

const props = defineProps({
  pois: { type: Array, default: () => [] },
  weatherText: { type: String, default: "天气信息暂不可用" },
  activePoiId: { type: String, default: "" },
  routeTarget: { type: Object, default: null }
});

const emit = defineEmits(["select-poi", "search"]);

const mapEl = ref(null);
const loading = ref(true);
const error = ref("");
const keyword = ref("");
const routeMode = ref("driving");
const routeData = ref({});
const routeLoading = ref(false);
const showRoutePanel = ref(false);
const popupPoi = ref(null);
const popupStyle = ref({});

let map;
let markers = [];
let routePolylines = [];
let startMarker = null;
let startLngLat = null;

const START_ADDRESS = "武汉大学信息学部南二门";

const firstPoi = computed(() => props.pois[0] || null);

const routeModes = [
  { key: "driving", label: "驾车" },
  { key: "walking", label: "步行" },
  { key: "transit", label: "公交" }
];

function parseLocation(poi) {
  const value = poi?.location || poi?.raw?.location || "";
  const [lng, lat] = String(value).split(",").map(Number);
  return Number.isFinite(lng) && Number.isFinite(lat) ? [lng, lat] : null;
}

function loadScript(key, securityCode) {
  if (window.AMap) return Promise.resolve();
  if (!key) return Promise.reject(new Error("missing amap key"));
  window._AMapSecurityConfig = securityCode ? { securityJsCode: securityCode } : window._AMapSecurityConfig;
  const existing = document.querySelector("script[data-amap-jsapi]");
  if (existing) {
    return new Promise((resolve, reject) => {
      existing.addEventListener("load", resolve, { once: true });
      existing.addEventListener("error", reject, { once: true });
    });
  }
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.dataset.amapJsapi = "true";
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(key)}&plugin=AMap.Scale,AMap.ToolBar`;
    script.async = true;
    script.onload = resolve;
    script.onerror = () => reject(new Error("amap jsapi load failed"));
    document.head.appendChild(script);
  });
}

function openPopup(poi, lnglat) {
  if (!map) return;
  const pixel = map.lngLatToContainer(lnglat);
  popupStyle.value = { left: pixel.x + "px", top: pixel.y + "px" };
  popupPoi.value = poi;
}

function closePopup() {
  popupPoi.value = null;
}

function clearMarkers() {
  if (map && markers.length) map.remove(markers);
  markers = [];
}

function syncMarkers() {
  if (!map || !window.AMap) return;
  clearMarkers();
  props.pois.forEach((poi, index) => {
    const position = parseLocation(poi);
    if (!position) return;
    const marker = new window.AMap.Marker({
      position,
      anchor: "bottom-center",
      title: poi.name,
      content: `<button class="amap-pin ${poi.type === "钓场" ? "paid" : ""}" type="button"><span>${index + 1}</span></button>`
    });
    marker.on("click", (e) => {
      openPopup(poi, e.target.getPosition());
      emit("select-poi", poi);
    });
    markers.push(marker);
  });
  if (markers.length) {
    map.add(markers);
    map.setFitView(markers, false, [92, 26, 118, 26], 15);
  }
}

function clearRoutes() {
  if (routePolylines.length) {
    map.remove(routePolylines);
    routePolylines = [];
  }
  if (startMarker) {
    map.remove(startMarker);
    startMarker = null;
  }
  showRoutePanel.value = false;
  routeData.value = {};
}

function drawRoute(path, color) {
  const polyline = new window.AMap.Polyline({
    path,
    strokeColor: color,
    strokeWeight: 6,
    strokeOpacity: 0.8,
    lineJoin: "round",
    zIndex: 20
  });
  routePolylines.push(polyline);
  map.add(polyline);
}

async function planRoutes(target) {
  if (!map || !target) return;
  clearRoutes();
  closePopup();
  routeLoading.value = true;
  showRoutePanel.value = true;

  try {
    const plugins = ["AMap.Driving", "AMap.Walking", "AMap.Transfer", "AMap.Geocoder"];
    const missing = plugins.filter((p) => !window.AMap[p]);
    if (missing.length) {
      await new Promise((resolve, reject) => {
        window.AMap.plugin(missing, () => {
          missing.forEach((p) => { if (!window.AMap[p]) reject(new Error(`plugin ${p} load failed`)); });
          resolve();
        });
      });
    }

    if (!startLngLat) {
      const geocoder = new window.AMap.Geocoder();
      const result = await new Promise((resolve) => {
        geocoder.getLocation(START_ADDRESS, (status, res) => {
          resolve(status === "complete" && res.geocodes.length ? res.geocodes[0].location : null);
        });
      });
      if (!result) throw new Error("起点定位失败");
      startLngLat = [result.lng, result.lat];
    }

    const endPos = parseLocation(target);
    if (!endPos) throw new Error("钓点坐标无效");
    const start = new window.AMap.LngLat(startLngLat[0], startLngLat[1]);
    const end = new window.AMap.LngLat(endPos[0], endPos[1]);

    startMarker = new window.AMap.Marker({
      position: startLngLat,
      anchor: "center",
      content: '<div class="start-marker" title="武汉大学信息学部南二门">起</div>',
      zIndex: 30
    });
    map.add(startMarker);

    const results = {};

    await new Promise((resolve) => {
      const driving = new window.AMap.Driving({ map: null, policy: 0 });
      driving.search(start, end, (status, res) => {
        if (status === "complete" && res.routes?.length) {
          const route = res.routes[0];
          results.driving = { distance: route.distance, time: route.time, path: route.steps.flatMap((s) => s.path) };
        }
        resolve();
      });
    });

    await new Promise((resolve) => {
      const walking = new window.AMap.Walking({ map: null });
      walking.search(start, end, (status, res) => {
        if (status === "complete" && res.routes?.length) {
          const route = res.routes[0];
          results.walking = { distance: route.distance, time: route.time, path: route.steps.flatMap((s) => s.path) };
        }
        resolve();
      });
    });

    await new Promise((resolve) => {
      const transfer = new window.AMap.Transfer({ map: null, city: "武汉市", policy: 0 });
      transfer.search(start, end, (status, res) => {
        if (status === "complete" && res.plans?.length) {
          const plan = res.plans[0];
          results.transit = { distance: plan.distance, time: plan.time, path: plan.segments.flatMap((s) => s.path || []) };
        }
        resolve();
      });
    });

    routeData.value = results;

    if (results[routeMode.value]) {
      drawRoute(results[routeMode.value].path, getRouteColor(routeMode.value));
    }

    const allPaths = Object.values(results).flatMap((r) => r.path).filter(Boolean);
    if (allPaths.length) {
      map.setFitView([startMarker, ...markers], false, [80, 30, 80, 200], 13);
    }
  } catch (e) {
    error.value = e?.message || "路线规划失败";
  } finally {
    routeLoading.value = false;
  }
}

function getRouteColor(mode) {
  return { driving: "#315f86", walking: "#1f7a58", transit: "#f0b840" }[mode] || "#315f86";
}

function switchRouteMode(mode) {
  routeMode.value = mode;
  if (routePolylines.length) {
    map.remove(routePolylines);
    routePolylines = [];
  }
  const data = routeData.value[mode];
  if (data?.path?.length) {
    drawRoute(data.path, getRouteColor(mode));
    map.setFitView([startMarker, ...markers], false, [80, 30, 80, 200], 13);
  }
}

function formatDistance(m) {
  return m >= 1000 ? `${(m / 1000).toFixed(1)}km` : `${m}m`;
}

function formatTime(s) {
  return s >= 3600 ? `${Math.floor(s / 3600)}h${Math.round((s % 3600) / 60)}min` : `${Math.round(s / 60)}min`;
}

function closeRoute() {
  clearRoutes();
  if (markers.length) map.setFitView(markers, false, [92, 26, 118, 26], 15);
}

async function initMap() {
  loading.value = true;
  error.value = "";
  try {
    const config = await fetchAmapConfig();
    await loadScript(config.key, config.securityCode);
    const center = parseLocation(firstPoi.value) || [114.3055, 30.5928];
    map = new window.AMap.Map(mapEl.value, {
      center,
      zoom: 12,
      viewMode: "2D",
      mapStyle: "amap://styles/normal",
      resizeEnable: true
    });
    map.addControl(new window.AMap.Scale());
    map.addControl(new window.AMap.ToolBar({ position: "RT" }));
    syncMarkers();

    map.on("click", closePopup);
    map.on("mapmove", closePopup);
  } catch (reason) {
    error.value = reason?.message || "高德地图加载失败";
  } finally {
    loading.value = false;
  }
}

function submitSearch() {
  emit("search", keyword.value.trim());
}

onMounted(initMap);
onBeforeUnmount(() => {
  clearMarkers();
  clearRoutes();
  closePopup();
  if (map) { map.destroy(); map = null; }
});

watch(() => props.pois, () => { clearRoutes(); closePopup(); syncMarkers(); }, { deep: true });
watch(() => props.activePoiId, (id) => {
  if (!map || !id) return;
  const poi = props.pois.find((p) => p.id === id);
  if (!poi) return;
  const position = parseLocation(poi);
  if (!position) return;
  map.setZoomAndCenter(15, position);
  markers.forEach((m, i) => {
    const content = m.getContent();
    const isTarget = content && content.includes("active-pin");
    if (i === props.pois.findIndex((p) => p.id === id) && !isTarget) {
      const original = props.pois[i];
      m.setContent(`<button class="amap-pin active-pin ${original.type === "钓场" ? "paid" : ""}" type="button"><span>${i + 1}</span></button>`);
    } else if (i !== props.pois.findIndex((p) => p.id === id) && isTarget) {
      const original = props.pois[i];
      m.setContent(`<button class="amap-pin ${original.type === "钓场" ? "paid" : ""}" type="button"><span>${i + 1}</span></button>`);
    }
  });
});
watch(() => props.routeTarget, (target) => { if (target) planRoutes(target); });
</script>

<template>
  <section class="map-card">
    <div ref="mapEl" class="amap-stage" aria-label="高德地图"></div>

    <form class="map-search" @submit.prevent="submitSearch">
      <span aria-hidden="true">⌕</span>
      <input v-model="keyword" type="search" placeholder="搜索水库、河流、钓场、鱼种" />
    </form>

    <div class="weather-pill">{{ weatherText }}</div>

    <div v-if="loading" class="map-status">地图加载中</div>
    <div v-else-if="error" class="map-status error">
      <strong>高德地图暂不可用</strong>
      <span>{{ error }}</span>
    </div>

    <div v-if="firstPoi && !showRoutePanel && !popupPoi" class="recommend-strip">
      <strong>今日推荐：{{ firstPoi.name }}</strong>
      <p>{{ firstPoi.reason }}</p>
    </div>

    <Transition name="popup">
      <div v-if="popupPoi" class="poi-popup" :style="popupStyle" @click.stop>
        <div class="popup-head">
          <strong>{{ popupPoi.name }}</strong>
          <span class="popup-score">{{ popupPoi.score }}</span>
        </div>
        <p class="popup-meta">{{ popupPoi.type }} · {{ popupPoi.distance }} · {{ (popupPoi.fish || []).join(" / ") }}</p>
        <p class="popup-reason">{{ popupPoi.reason }}</p>
        <div v-if="popupPoi.tags?.length" class="popup-tags">
          <span v-for="tag in popupPoi.tags" :key="tag" class="popup-tag">{{ tag }}</span>
        </div>
      </div>
    </Transition>

    <div v-if="showRoutePanel" class="route-panel">
      <div class="route-header">
        <span class="route-title">{{ START_ADDRESS }} → {{ props.routeTarget?.name }}</span>
        <button class="route-close" type="button" @click="closeRoute">✕</button>
      </div>
      <div class="route-tabs">
        <button
          v-for="mode in routeModes" :key="mode.key"
          :class="{ active: routeMode === mode.key }"
          type="button"
          class="route-tab"
          @click="switchRouteMode(mode.key)"
        >
          <span class="route-mode-icon" :style="{ background: getRouteColor(mode.key) }"></span>
          {{ mode.label }}
          <template v-if="routeData[mode.key]">
            <span class="route-stat">{{ formatDistance(routeData[mode.key].distance) }}</span>
            <span class="route-stat">{{ formatTime(routeData[mode.key].time) }}</span>
          </template>
          <span v-else class="route-stat">—</span>
        </button>
      </div>
      <div v-if="routeLoading" class="route-loading">路线规划中…</div>
    </div>
  </section>
</template>
