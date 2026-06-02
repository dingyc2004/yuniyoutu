<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from "vue";
import CommunityView from "./components/CommunityView.vue";
import MapPanel from "./components/MapPanel.vue";
import MineView from "./components/MineView.vue";
import PoiCard from "./components/PoiCard.vue";
import PublishView from "./components/PublishView.vue";
import TutorialsView from "./components/TutorialsView.vue";
import { seedData } from "./data/seedData";
import { fetchCollection, fetchFishSpecies } from "./services/api";

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
const galleryIndex = ref(0);
const fishProfile = ref(null);
const fishGalleryIndex = ref(0);
const toast = ref("");
let toastTimer;
let galleryTimer;

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

const detailGallery = computed(() => {
  if (!detailPoi.value) return [];
  const poi = detailPoi.value;
  const imageUrls = Array.isArray(poi.images) ? poi.images.filter(Boolean) : [];
  if (imageUrls.length) {
    return imageUrls.map((url, index) => ({
      id: `${poi.id || poi.name}-image-${index}`,
      title: `${poi.name} · ${index + 1}`,
      subtitle: poi.address || poi.type,
      url
    }));
  }
  return [
    {
      id: `${poi.id || poi.name}-waterside`,
      title: "水域环境",
      subtitle: poi.name,
      tone: "green"
    },
    {
      id: `${poi.id || poi.name}-shore`,
      title: "岸线入口",
      subtitle: poi.address || "位置待确认",
      tone: "blue"
    },
    {
      id: `${poi.id || poi.name}-catch`,
      title: "鱼获参考",
      subtitle: (poi.fish || []).join(" / ") || "暂无鱼种数据",
      tone: "amber"
    }
  ];
});

const fishGallery = computed(() => fishProfile.value?.gallery || []);

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
  galleryIndex.value = 0;
  detailPoi.value = poi;
}

function closeDetail() {
  detailPoi.value = null;
}

async function openFishProfile(fishName) {
  fishGalleryIndex.value = 0;
  const profile = await fetchFishSpecies(fishName);
  if (!profile) {
    showToast(`暂未收录：${fishName}`);
    return;
  }
  fishProfile.value = profile;
}

function closeFishProfile() {
  fishProfile.value = null;
}

function showFishGallerySlide(index) {
  const total = fishGallery.value.length;
  if (!total) return;
  fishGalleryIndex.value = (index + total) % total;
}

function nextFishGallerySlide() {
  showFishGallerySlide(fishGalleryIndex.value + 1);
}

function previousFishGallerySlide() {
  showFishGallerySlide(fishGalleryIndex.value - 1);
}

function showGallerySlide(index) {
  const total = detailGallery.value.length;
  if (!total) return;
  galleryIndex.value = (index + total) % total;
}

function nextGallerySlide() {
  showGallerySlide(galleryIndex.value + 1);
}

function previousGallerySlide() {
  showGallerySlide(galleryIndex.value - 1);
}

function startGalleryPlayback() {
  window.clearInterval(galleryTimer);
  if (detailGallery.value.length <= 1) return;
  galleryTimer = window.setInterval(nextGallerySlide, 3200);
}

function stopGalleryPlayback() {
  window.clearInterval(galleryTimer);
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
onBeforeUnmount(stopGalleryPlayback);

watch(detailPoi, (poi) => {
  stopGalleryPlayback();
  if (poi) startGalleryPlayback();
});
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
            <PoiCard
              v-for="poi in shownPois"
              :key="poi.id"
              :poi="poi"
              @select="focusPoi"
              @navigate="startNav"
              @detail="openDetail"
              @fish-detail="openFishProfile"
            />
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
      <div v-if="detailPoi" class="modal-overlay" @click.self="closeDetail">
        <article class="detail-card">
          <button class="detail-close" type="button" @click="closeDetail">✕</button>

          <section class="detail-gallery" aria-label="钓点图片集">
            <div
              v-for="(slide, index) in detailGallery"
              :key="slide.id"
              :class="['gallery-slide', `tone-${slide.tone || 'green'}`, { active: index === galleryIndex }]"
            >
              <img v-if="slide.url" :src="slide.url" :alt="slide.title" />
              <div v-else class="gallery-fallback">
                <span>{{ slide.title }}</span>
                <strong>{{ slide.subtitle }}</strong>
              </div>
            </div>

            <button class="gallery-control previous" type="button" aria-label="上一张" @click="previousGallerySlide">‹</button>
            <button class="gallery-control next" type="button" aria-label="下一张" @click="nextGallerySlide">›</button>

            <div class="gallery-dots" aria-label="图片位置">
              <button
                v-for="(_, index) in detailGallery"
                :key="index"
                :class="{ active: index === galleryIndex }"
                type="button"
                :aria-label="`查看第 ${index + 1} 张`"
                @click="showGallerySlide(index)"
              ></button>
            </div>
          </section>

          <div class="detail-hero">
            <span class="detail-score">{{ detailPoi.score }}</span>
            <span class="detail-type">{{ detailPoi.type }}</span>
          </div>
          <h2>{{ detailPoi.name }}</h2>
          <p class="detail-address" v-if="detailPoi.address">{{ detailPoi.address }}</p>
          <p class="detail-distance">{{ detailPoi.distance }}</p>
          <div class="source-row">
            <span class="source-pill">{{ detailPoi.source || "平台整理" }}</span>
            <span class="meta">{{ detailPoi.category || "垂钓点位" }}</span>
          </div>

          <div class="detail-section">
            <h4>安全提示</h4>
            <p>{{ detailPoi.risk }}</p>
          </div>

          <div class="detail-section" v-if="detailPoi.fish?.length">
            <h4>常见鱼种</h4>
            <div class="chips compact">
              <button
                v-for="f in detailPoi.fish"
                :key="f"
                class="badge fish-badge"
                type="button"
                @click="openFishProfile(f)"
              >
                {{ f }}
              </button>
            </div>
          </div>

          <div class="detail-section" v-if="detailPoi.tags?.length">
            <h4>标签</h4>
            <div class="chips compact">
              <span v-for="tag in detailPoi.tags" :key="tag" class="badge tag-badge">{{ tag }}</span>
            </div>
          </div>
        </article>
      </div>
    </Transition>

    <Transition name="modal">
      <div v-if="fishProfile" class="modal-overlay fish-overlay" @click.self="closeFishProfile">
        <article class="detail-card fish-card">
          <button class="detail-close" type="button" @click="closeFishProfile">✕</button>

          <section class="detail-gallery fish-gallery" aria-label="鱼种图片集">
            <div
              v-for="(slide, index) in fishGallery"
              :key="`${fishProfile.id}-slide-${index}`"
              :class="['gallery-slide', `tone-${slide.tone || 'green'}`, { active: index === fishGalleryIndex }]"
            >
              <img v-if="slide.url" :src="slide.url" :alt="slide.title" />
              <div v-else class="gallery-fallback">
                <span>{{ slide.title }}</span>
                <strong>{{ slide.subtitle }}</strong>
              </div>
            </div>

            <button class="gallery-control previous" type="button" aria-label="上一张" @click="previousFishGallerySlide">‹</button>
            <button class="gallery-control next" type="button" aria-label="下一张" @click="nextFishGallerySlide">›</button>

            <div class="gallery-dots" aria-label="图片位置">
              <button
                v-for="(_, index) in fishGallery"
                :key="index"
                :class="{ active: index === fishGalleryIndex }"
                type="button"
                :aria-label="`查看第 ${index + 1} 张`"
                @click="showFishGallerySlide(index)"
              ></button>
            </div>
          </section>

          <p class="eyebrow">FISH GUIDE</p>
          <h2>{{ fishProfile.name }}</h2>
          <p v-if="fishProfile.alias?.length" class="meta">别名：{{ fishProfile.alias.join(" / ") }}</p>

          <div class="fish-stats">
            <div>
              <span>常见体长</span>
              <strong>{{ fishProfile.length }}</strong>
            </div>
            <div>
              <span>常见重量</span>
              <strong>{{ fishProfile.weight }}</strong>
            </div>
          </div>

          <div class="detail-section">
            <h4>习性</h4>
            <p>{{ fishProfile.habits }}</p>
          </div>

          <div class="detail-section">
            <h4>攻略</h4>
            <ul class="fish-strategy">
              <li v-for="tip in fishProfile.strategy" :key="tip">{{ tip }}</li>
            </ul>
          </div>

          <div class="detail-section">
            <h4>活跃季节</h4>
            <p>{{ fishProfile.season }}</p>
          </div>

          <div class="detail-section">
            <h4>提醒</h4>
            <p>{{ fishProfile.risk_note }}</p>
          </div>
        </article>
      </div>
    </Transition>
  </main>
</template>
