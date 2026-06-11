<script setup>
import { computed, ref } from "vue";
import { ArrowLeft, ArrowRight, Location, MapLocation, Notebook } from "@element-plus/icons-vue";
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

const live = computed(() => props.weather?.live || props.weather || {});
const fishingIndex = computed(() => props.weather?.fishingIndex ?? 72);
const bestWindow = computed(() => props.weather?.bestWindow || "建议关注风力与窗口期变化");
const todayRecommend = computed(() => props.weather?.todayRecommend || {});

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
const pressure = computed(() => live.value.pressure || live.value.pressure_hpa || "1012");

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

function shortReason(poi) {
  const reason = poi?.reason || "查看鱼情、交通和安全提示";
  return reason.length > 20 ? `${reason.slice(0, 20)}...` : reason;
}

function mapPinStyle(poi, index) {
  if (poi?.x && poi?.y) {
    return { left: `${poi.x}%`, top: `${poi.y}%` };
  }
  const fallback = [
    { left: "66%", top: "38%" },
    { left: "30%", top: "56%" },
    { left: "74%", top: "72%" },
    { left: "42%", top: "34%" },
    { left: "58%", top: "80%" }
  ];
  return fallback[index % fallback.length];
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

  <section v-else class="home-page">
    <section class="home-fit-card" aria-label="今日适钓">
      <div class="home-fit-top">
        <div>
          <p class="home-fit-city">{{ cityLabel }}</p>
          <p class="home-fit-weather">{{ live.weather || "多云" }} · {{ temperature }}℃</p>
        </div>
        <div class="home-fit-index" aria-label="适钓指数">
          <span class="home-fit-index-label">适钓指数</span>
          <strong class="home-fit-index-value">{{ fishingIndex }}</strong>
        </div>
      </div>
      <div class="home-fit-meta">
        <span>风力 {{ windLabel }}</span>
        <span>气压 {{ pressure }} hPa</span>
        <span>湿度 {{ live.humidity || "--" }}%</span>
      </div>
      <p class="home-fit-advice">{{ bestWindow }}</p>
    </section>

    <section class="home-section">
      <div class="home-section-head">
        <h2>今日推荐</h2>
      </div>
      <div class="home-rec-grid">
        <div class="home-rec-item">
          <span>推荐目标</span>
          <strong>{{ todayRecommend.species || "鲫鱼" }}</strong>
        </div>
        <div class="home-rec-item">
          <span>推荐钓法</span>
          <strong>{{ todayRecommend.method || "台钓" }}</strong>
        </div>
        <div class="home-rec-item wide">
          <span>推荐时段</span>
          <strong>{{ todayRecommend.timeWindow || "06:30-09:00" }}</strong>
          <small v-if="todayRecommend.note">{{ todayRecommend.note }}</small>
        </div>
      </div>
    </section>

    <section class="home-section">
      <div class="home-section-head">
        <h2>附近钓点</h2>
        <button type="button" class="home-text-btn" @click="openMap">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </button>
      </div>
      <div class="home-poi-rail" aria-label="附近钓点列表">
        <article
          v-for="(poi, index) in nearbyPois"
          :key="poi.id"
          class="home-poi-card"
          @click="openPoi(poi)"
        >
          <div :class="['home-poi-cover', `tone-${poiTone(poi, index)}`]">
            <span class="home-poi-type">{{ poi.type }}</span>
          </div>
          <div class="home-poi-body">
            <strong>{{ poi.name }}</strong>
            <p>{{ poi.distance }} · 热度 {{ poi.score }}</p>
            <span class="home-poi-bite">{{ shortReason(poi) }}</span>
          </div>
        </article>
      </div>
    </section>

    <section class="home-section">
      <div class="home-section-head">
        <h2>钓点地图</h2>
        <button type="button" class="home-text-btn" @click="openMap">
          展开地图
          <el-icon><MapLocation /></el-icon>
        </button>
      </div>
      <button type="button" class="home-map-preview" @click="openMap">
        <div class="home-map-canvas">
          <span class="home-map-you"><el-icon><Location /></el-icon></span>
          <span
            v-for="(poi, index) in nearbyPois.slice(0, 5)"
            :key="poi.id"
            class="home-map-pin"
            :style="mapPinStyle(poi, index)"
            :title="poi.name"
          ></span>
        </div>
        <div class="home-map-caption">
          <strong>附近 {{ pois.length }} 个钓点</strong>
          <span>{{ nearbyPois[0]?.name || "打开地图查看可钓区域" }}</span>
        </div>
      </button>
    </section>

    <section class="home-quick-start">
      <el-button class="home-start-btn" type="primary" round size="large" @click="startRecord">
        开始钓鱼
      </el-button>
      <el-button class="home-records-btn" round size="large" :icon="Notebook" @click="viewRecords">
        我的记录
        <span v-if="records.length" class="home-records-count">{{ records.length }}</span>
      </el-button>
    </section>
  </section>
</template>
