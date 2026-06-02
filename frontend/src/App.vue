<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import CommunityView from "./components/CommunityView.vue";
import MapPanel from "./components/MapPanel.vue";
import MineView from "./components/MineView.vue";
import PoiCard from "./components/PoiCard.vue";
import PublishView from "./components/PublishView.vue";
import TutorialsView from "./components/TutorialsView.vue";
import { seedData } from "./data/seedData";
import { fetchCollection } from "./services/api";

const tabs = [
  { id: "map", label: "地图", icon: "⌖" },
  { id: "community", label: "社区", icon: "◐" },
  { id: "publish", label: "发布", icon: "+" },
  { id: "tutorials", label: "教程", icon: "▣" },
  { id: "mine", label: "我的", icon: "◉" }
];

const titles = {
  map: "附近钓点",
  community: "鱼获社区",
  publish: "记一竿",
  tutorials: "钓鱼教程",
  mine: "我的战绩"
};

const filters = ["全部", "野钓", "钓场", "路亚", "免费", "夜钓"];
const activeTab = ref("map");
const activeFilter = ref("全部");
const selectedPoiId = ref("");
const navTarget = ref(null);
const detailPoi = ref(null);
const toast = ref("");
let toastTimer;

const state = reactive({
  pois: seedData.pois,
  feed: seedData.feed,
  tutorials: seedData.tutorials,
  weather: seedData.weather
});

const weatherText = computed(() => {
  const live = state.weather?.live || state.weather;
  if (!live) return "天气信息暂不可用";
  const direction = live.winddirection || live.wind_direction || "风向未知";
  const windLevel = live.windpower || live.wind_level;
  const temperature = live.temperature || live.temperature_c || live.feels_like_c || "";
  const wind = windLevel ? `${windLevel}级` : "";
  return `${live.weather} · ${temperature}℃ · ${direction} ${wind}`;
});

const shownPois = computed(() => {
  if (activeFilter.value === "全部") return state.pois;
  return state.pois.filter((poi) => poi.type === activeFilter.value || (poi.tags || []).includes(activeFilter.value));
});

function showToast(message) {
  toast.value = message;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => { toast.value = ""; }, 1800);
}

async function searchPois(keyword) {
  const query = keyword ? `keyword=${encodeURIComponent(keyword)}` : "city=420100";
  state.pois = await fetchCollection(`/api/pois?${query}`, "pois");
  activeFilter.value = "全部";
  showToast(keyword ? `已搜索：${keyword}` : "已刷新附近钓点");
}

function selectPoi(poi) {
  selectedPoiId.value = poi.id;
  showToast(`${poi.name} · 推荐分 ${poi.score}`);
}

function focusPoi(poi) {
  selectedPoiId.value = poi.id;
  const mapEl = document.querySelector(".map-card");
  if (mapEl) mapEl.scrollIntoView({ behavior: "smooth" });
  showToast(`已定位：${poi.name}`);
}

function startNav(poi) {
  navTarget.value = { ...poi };
  const mapEl = document.querySelector(".map-card");
  if (mapEl) mapEl.scrollIntoView({ behavior: "smooth" });
}

function openDetail(poi) {
  detailPoi.value = poi;
}

async function loadInitialData() {
  const [pois, feed, tutorials, weather] = await Promise.all([
    fetchCollection("/api/pois?city=420100", "pois"),
    fetchCollection("/api/feed", "feed"),
    fetchCollection("/api/tutorials", "tutorials"),
    fetchCollection("/api/weather?city=420100", "weather")
  ]);
  state.pois = pois;
  state.feed = feed;
  state.tutorials = tutorials;
  state.weather = weather;
}

onMounted(loadInitialData);
</script>

<template>
  <main class="app-shell">
    <section class="topbar">
      <div>
        <p class="eyebrow">YUNI MAP</p>
        <h1>{{ titles[activeTab] }}</h1>
      </div>
      <button class="icon-btn" type="button" aria-label="定位" @click="showToast('已使用示例定位：武汉市洪山区')">⌖</button>
    </section>

    <section class="screen">
      <template v-if="activeTab === 'map'">
        <MapPanel
          :pois="state.pois"
          :active-poi-id="selectedPoiId"
          :route-target="navTarget"
          :weather-text="weatherText"
          @select-poi="selectPoi"
          @search="searchPois"
        />

        <div class="chips">
          <button v-for="filter in filters" :key="filter" :class="{ active: activeFilter === filter }" class="chip" type="button" @click="activeFilter = filter">
            {{ filter }}
          </button>
        </div>

        <section class="section">
          <div class="section-head">
            <h2>附近可去</h2>
            <span class="meta">{{ weatherText }}</span>
          </div>
          <div class="poi-list">
            <PoiCard v-for="poi in shownPois" :key="poi.id" :poi="poi" @select="focusPoi" @navigate="startNav" @detail="openDetail" />
          </div>
        </section>
      </template>

      <CommunityView v-else-if="activeTab === 'community'" :feed="state.feed" @action="showToast" />
      <PublishView v-else-if="activeTab === 'publish'" :pois="state.pois" @action="showToast" />
      <TutorialsView v-else-if="activeTab === 'tutorials'" :tutorials="state.tutorials" @action="showToast" />
      <MineView v-else />
    </section>

    <nav class="tabbar" aria-label="主导航">
      <button v-for="tab in tabs" :key="tab.id" :class="{ active: activeTab === tab.id, 'publish-tab': tab.id === 'publish' }" class="tab" type="button" @click="activeTab = tab.id">
        <span>{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </nav>

    <Transition name="toast">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </Transition>

    <Transition name="modal">
      <div v-if="detailPoi" class="modal-overlay" @click.self="detailPoi = null">
        <article class="detail-card">
          <button class="detail-close" type="button" @click="detailPoi = null">✕</button>
          <div class="detail-hero">
            <span class="detail-score">{{ detailPoi.score }}</span>
            <span class="detail-type">{{ detailPoi.type }}</span>
          </div>
          <h2>{{ detailPoi.name }}</h2>
          <p class="detail-address" v-if="detailPoi.address">{{ detailPoi.address }}</p>
          <p class="detail-distance">{{ detailPoi.distance }}</p>

          <div class="detail-section">
            <h4>推荐理由</h4>
            <p>{{ detailPoi.reason }}</p>
          </div>

          <div class="detail-section">
            <h4>安全提示</h4>
            <p>{{ detailPoi.risk }}</p>
          </div>

          <div class="detail-section" v-if="detailPoi.fish?.length">
            <h4>常见鱼种</h4>
            <div class="chips compact">
              <span v-for="f in detailPoi.fish" :key="f" class="badge">{{ f }}</span>
            </div>
          </div>

          <div class="detail-section" v-if="detailPoi.tags?.length">
            <h4>标签</h4>
            <div class="chips compact">
              <span v-for="tag in detailPoi.tags" :key="tag" class="badge">{{ tag }}</span>
            </div>
          </div>
        </article>
      </div>
    </Transition>
  </main>
</template>
