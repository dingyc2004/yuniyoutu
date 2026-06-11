<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { Close, Search } from "@element-plus/icons-vue";
import { fetchAmapConfig } from "../services/api";

const props = defineProps({
  open: { type: Boolean, default: false },
  latitude: { type: Number, default: null },
  longitude: { type: Number, default: null },
  locationName: { type: String, default: "等待定位" }
});

const emit = defineEmits([
  "update:open",
  "update:latitude",
  "update:longitude",
  "update:locationName",
  "action"
]);

const mapEl = ref(null);
const loading = ref(false);
const locating = ref(false);
const error = ref("");
const searchKeyword = ref("");

const DEFAULT_CENTER = [114.3055, 30.5928];

let map = null;
let marker = null;
let geocoder = null;

const draftLocationName = computed({
  get: () => props.locationName,
  set: (value) => emit("update:locationName", value)
});

function loadScript(key, securityCode) {
  if (securityCode) {
    window._AMapSecurityConfig = { securityJsCode: securityCode };
  }
  if (window.AMap) return Promise.resolve();
  if (!key) return Promise.reject(new Error("missing amap key"));
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
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(key)}&plugin=AMap.Geocoder`;
    script.async = true;
    script.onload = resolve;
    script.onerror = () => reject(new Error("amap jsapi load failed"));
    document.head.appendChild(script);
  });
}

function emitCoords(lat, lng, name) {
  emit("update:latitude", lat);
  emit("update:longitude", lng);
  if (name) emit("update:locationName", name);
}

function setMarker(lng, lat, zoomTo = true) {
  if (!map || !window.AMap) return;
  const pos = [lng, lat];
  if (!marker) {
    marker = new window.AMap.Marker({ position: pos, anchor: "center" });
    map.add(marker);
  } else {
    marker.setPosition(pos);
  }
  if (zoomTo) map.setZoomAndCenter(Math.max(map.getZoom(), 15), pos);
}

function resolveAddress(lng, lat, fallback) {
  if (!geocoder) {
    emitCoords(lat, lng, fallback || props.locationName || "地图选点");
    return;
  }
  geocoder.getAddress([lng, lat], (status, result) => {
    const name =
      status === "complete" && result.regeocode
        ? result.regeocode.formattedAddress
        : fallback || props.locationName || "地图选点";
    emitCoords(lat, lng, name);
  });
}

function onMapClick(event) {
  const lng = Number(event.lnglat.lng.toFixed(6));
  const lat = Number(event.lnglat.lat.toFixed(6));
  setMarker(lng, lat, false);
  resolveAddress(lng, lat);
  emit("action", "已在地图上更新选点");
}

function submitSearch() {
  const keyword = searchKeyword.value.trim();
  if (!keyword) {
    emit("action", "请输入要搜索的位置");
    return;
  }
  draftLocationName.value = keyword;
  emit("action", `已填写位置：${keyword}`);
}

async function ensureGeocoder() {
  if (geocoder) return;
  const config = await fetchAmapConfig();
  await loadScript(config.key, config.securityCode);
  await new Promise((resolve) => {
    window.AMap.plugin("AMap.Geocoder", () => {
      geocoder = new window.AMap.Geocoder();
      resolve();
    });
  });
}

function locateCurrentPosition() {
  if (locating.value) return;
  if (!navigator.geolocation) {
    emit("action", "当前浏览器不支持定位");
    return;
  }
  locating.value = true;
  navigator.geolocation.getCurrentPosition(
    async (position) => {
      try {
        const lat = Number(position.coords.latitude.toFixed(6));
        const lng = Number(position.coords.longitude.toFixed(6));
        emitCoords(lat, lng, "当前位置");
        if (!geocoder) {
          try {
            await ensureGeocoder();
          } catch {
            /* 保留经纬度 */
          }
        }
        setMarker(lng, lat);
        resolveAddress(lng, lat);
        emit("action", "已获取当前位置");
      } finally {
        locating.value = false;
      }
    },
    (geoError) => {
      locating.value = false;
      const message =
        geoError.code === 1
          ? "定位未授权，请在浏览器设置中允许位置权限"
          : "定位失败，请稍后重试或在地图上手动选点";
      emit("action", message);
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
}

function destroyMap() {
  if (marker) {
    marker.setMap(null);
    marker = null;
  }
  if (map) {
    map.destroy();
    map = null;
  }
}

async function initMap() {
  if (!mapEl.value) return;
  destroyMap();
  loading.value = true;
  error.value = "";
  try {
    const config = await fetchAmapConfig();
    if (!config.key || !config.securityCode) throw new Error("map unavailable");
    await loadScript(config.key, config.securityCode);
    const center =
      Number.isFinite(props.longitude) && Number.isFinite(props.latitude)
        ? [props.longitude, props.latitude]
        : DEFAULT_CENTER;
    map = new window.AMap.Map(mapEl.value, {
      center,
      zoom: 14,
      viewMode: "2D",
      mapStyle: "amap://styles/normal",
      resizeEnable: true
    });
    map.on("click", onMapClick);
    map.on("complete", () => {
      map?.resize();
    });
    if (!geocoder) {
      window.AMap.plugin("AMap.Geocoder", () => {
        geocoder = new window.AMap.Geocoder();
      });
    }
    if (Number.isFinite(props.longitude) && Number.isFinite(props.latitude)) {
      setMarker(props.longitude, props.latitude, false);
    }
    await new Promise((resolve) => requestAnimationFrame(resolve));
    map.resize();
  } catch (reason) {
    error.value = "可以先手动填写位置名称";
    destroyMap();
  } finally {
    loading.value = false;
  }
}

function closeDialog() {
  emit("update:open", false);
  destroyMap();
}

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      await nextTick();
      await new Promise((resolve) => requestAnimationFrame(resolve));
      await initMap();
      if (map) setTimeout(() => map?.resize(), 120);
    } else {
      destroyMap();
    }
  }
);

watch(
  () => [props.latitude, props.longitude],
  ([lat, lng]) => {
    if (!map || !Number.isFinite(lat) || !Number.isFinite(lng)) return;
    setMarker(lng, lat, false);
  }
);

onBeforeUnmount(() => {
  destroyMap();
  geocoder = null;
});
</script>

<template>
  <div v-if="open" class="record-dialog-backdrop" @click.self="closeDialog">
    <section class="record-dialog card record-location-dialog" role="dialog" aria-modal="true" aria-labelledby="location-dialog-title">
      <div class="dialog-head">
        <h2 id="location-dialog-title">选择位置</h2>
        <button class="mini-btn icon-only" type="button" aria-label="关闭" @click="closeDialog">
          <el-icon><Close /></el-icon>
        </button>
      </div>

      <div class="record-location-dialog-actions">
        <button class="mini-btn" type="button" :disabled="locating || loading" @click="locateCurrentPosition">
          {{ locating ? "定位中..." : "自动定位" }}
        </button>
      </div>

      <form class="record-map-search" @submit.prevent="submitSearch">
        <el-icon aria-hidden="true"><Search /></el-icon>
        <el-input v-model="searchKeyword" type="search" placeholder="搜索位置、水域、地标" clearable />
        <el-button native-type="submit" type="primary" round>搜索</el-button>
      </form>

      <div class="record-map-card">
        <div ref="mapEl" class="record-map-stage" aria-label="地图选点" />
        <div v-if="loading" class="map-status record-map-status">地图加载中</div>
        <div v-else-if="error" class="map-status record-map-status error">
          <strong>暂时无法显示地图</strong>
          <span>{{ error }}</span>
        </div>
      </div>

      <label class="field">
        <span>位置名称</span>
        <input v-model="draftLocationName" placeholder="例如 东湖听涛岸边" />
      </label>
      <p class="meta record-coords">{{ latitude ?? "--" }}, {{ longitude ?? "--" }}</p>
      <p class="meta record-map-hint">可点击地图选点，也可以直接填写位置名称。</p>

      <button class="btn" type="button" @click="closeDialog">确定</button>
    </section>
  </div>
</template>
