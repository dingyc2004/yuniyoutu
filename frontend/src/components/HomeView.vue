<script setup>
import { computed, ref } from "vue";
import { ArrowLeft, ArrowRight, Location, Notebook } from "@element-plus/icons-vue";
import MapPanel from "./MapPanel.vue";

const props = defineProps({
  weather: { type: Object, default: () => ({}) },
  weatherText: { type: String, default: "天气待更新" },
  pois: { type: Array, default: () => [] },
  records: { type: Array, default: () => [] }
});

const emit = defineEmits(["action", "navigate", "search-pois"]);

const view = ref("main");
const selectedPoiId = ref("");
const sheetCollapsed = ref(false);

const live = computed(() => props.weather?.live || props.weather || {});
const fishingIndex = computed(() => props.weather?.fishingIndex ?? 72);
const bestWindow = computed(() => props.weather?.bestWindow || "建议关注风力与窗口期变化");

const cityLabel = computed(() => {
  const city = live.value.city || "武汉";
  return city.replace(/市$/, "");
});

const temperature = computed(() => live.value.temperature ?? live.value.temperature_c ?? "--");
const windLabel = computed(() => {
  const dir = live.value.winddirection || live.value.wind_direction || "";
  const power = live.value.windpower || live.value.wind_level;
  if (!dir && !power) return "--";
  return power ? `${dir}风 ${power}级` : `${dir}风`;
});
const nearbyPois = computed(() => [...props.pois].sort((a, b) => (b.score || 0) - (a.score || 0)).slice(0, 8));

const selectedPoi = computed(
  () => props.pois.find((poi) => poi.id === selectedPoiId.value) || props.pois[0]
);

const poiComments = [
  { id: "c1", author: "江风路亚", text: "清晨窗口期更稳定，岸边防滑要注意。" },
  { id: "c2", author: "不空军的阿明", text: "最近小鱼闹窝明显，建议饵料别太腥。" }
];

const toneCycle = ["blue", "green", "amber", "purple"];

function poiTone(poi, index = 0) {
  return poi?.coverTone || toneCycle[index % toneCycle.length];
}

function openPoi(poi) {
  selectedPoiId.value = poi.id;
  view.value = "poi-detail";
}

function openMap() {
  view.value = "map";
}

function backToMain() {
  view.value = "main";
}

function startRecord() {
  emit("navigate", "record");
}

function viewRecords() {
  emit("navigate", "record");
  emit("action", props.records.length ? `已有 ${props.records.length} 条记录` : "开始记录你的第一竿");
}

function confirmSpot(poi) {
  emit("action", `已选中 ${poi.name}，可前往记录页开始计时`);
}

function collapseMapSheet() {
  sheetCollapsed.value = true;
}

function expandMapSheet() {
  sheetCollapsed.value = false;
}
</script>

<template>
  <section v-if="view === 'map'" class="home-page home-subview">
    <header class="home-map-head">
      <button type="button" class="home-map-back" aria-label="返回首页" @click="backToMain">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <div>
        <h2>钓点地图</h2>
        <p>查看附近钓点与水情</p>
      </div>
    </header>
    <MapPanel
      class="home-map-full"
      :pois="pois"
      :weather-text="weatherText"
      @select-poi="openPoi"
      @search="(kw) => emit('search-pois', kw)"
    />
  </section>

  <section v-else-if="view === 'poi-detail' && selectedPoi" class="home-page home-subview">
    <el-button text class="back-link" :icon="ArrowLeft" @click="backToMain">返回首页</el-button>
    <article class="spot-detail home-spot-detail">
      <div :class="['spot-cover', 'home-spot-cover', `tone-${poiTone(selectedPoi)}`]">
        <span>{{ selectedPoi.type }}</span>
        <strong>{{ selectedPoi.name }}</strong>
      </div>
      <div class="spot-body">
        <div class="poi-head">
          <div>
            <h2>{{ selectedPoi.name }}</h2>
            <p class="meta">{{ selectedPoi.distance }} · 热度 {{ selectedPoi.score }}</p>
          </div>
          <el-tag round effect="plain" type="primary">热度 {{ selectedPoi.score }}</el-tag>
        </div>
        <p class="spot-copy">{{ selectedPoi.reason }}</p>
        <p class="meta">{{ selectedPoi.address }}</p>
        <div v-if="selectedPoi.fish?.length" class="chips compact">
          <el-tag v-for="fish in selectedPoi.fish" :key="fish" round effect="light">{{ fish }}</el-tag>
        </div>
        <section class="detail-section">
          <h4>钓友评论</h4>
          <div class="comment-list">
            <div v-for="comment in poiComments" :key="comment.id" class="comment-item">
              <strong>{{ comment.author }}</strong>
              <p>{{ comment.text }}</p>
            </div>
          </div>
        </section>
      </div>
    </article>
    <div class="home-cta-row">
      <el-button type="primary" round size="large" @click="startRecord">在此开始记录</el-button>
      <el-button round size="large" @click="confirmSpot(selectedPoi)">确认钓点</el-button>
    </div>
  </section>

  <section v-else class="home-page home-map-dashboard">
    <MapPanel
      class="home-map-hero"
      :pois="pois"
      :weather-text="weatherText"
      @select-poi="openPoi"
      @search="(kw) => emit('search-pois', kw)"
      @map-interaction="collapseMapSheet"
    />

    <header class="home-map-brand">
      <div>
        <span class="home-map-kicker">FISHMAN · EXPLORE</span>
        <strong>鱼你有图</strong>
      </div>
      <button type="button" class="home-map-city" @click="openMap">
        <el-icon><Location /></el-icon>
        {{ cityLabel }}
      </button>
    </header>

    <section class="home-map-intel" aria-label="今日适钓">
      <div class="home-intel-score">
        <span>适钓指数</span>
        <strong>{{ fishingIndex }}</strong>
      </div>
      <div class="home-intel-copy">
        <strong>{{ live.weather || "多云" }} · {{ temperature }}℃ · {{ windLabel }}</strong>
        <span>{{ bestWindow }}</span>
      </div>
      <button type="button" aria-label="展开地图" @click="openMap">
        <el-icon><ArrowRight /></el-icon>
      </button>
    </section>

    <section class="home-map-sheet" :class="{ collapsed: sheetCollapsed }" @click="sheetCollapsed && expandMapSheet()">
      <div class="home-sheet-handle"></div>
      <div class="home-sheet-head">
        <div>
          <span>NEARBY WATER</span>
          <h2>附近高活跃钓点</h2>
        </div>
        <strong class="home-sheet-count">{{ pois.length }} 个钓点 · 热力已显示</strong>
      </div>
      <div class="home-poi-rail home-poi-rail-map" aria-label="附近钓点列表">
        <article
          v-for="(poi, index) in nearbyPois.slice(0, 5)"
          :key="poi.id"
          class="home-poi-card"
          @click="openPoi(poi)"
        >
          <div :class="['home-poi-cover', `tone-${poiTone(poi, index)}`]">
            <span class="home-poi-type">{{ poi.type }}</span>
            <b>{{ poi.score }}</b>
          </div>
          <div class="home-poi-body">
            <strong>{{ poi.name }}</strong>
            <p>{{ poi.distance }} · {{ (poi.fish || []).slice(0, 2).join(" / ") || "鱼情待探" }}</p>
          </div>
        </article>
      </div>

      <div class="home-action-dock">
        <button type="button" class="home-start-action" @click="startRecord">
          <span class="home-action-icon"><el-icon><Location /></el-icon></span>
          <span>
            <small>START SESSION</small>
            <strong>开始钓鱼</strong>
          </span>
          <el-icon><ArrowRight /></el-icon>
        </button>
        <button type="button" class="home-record-action" @click="viewRecords">
          <el-icon><Notebook /></el-icon>
          <span>记录</span>
          <b>{{ records.length }}</b>
        </button>
      </div>
    </section>
  </section>
</template>
