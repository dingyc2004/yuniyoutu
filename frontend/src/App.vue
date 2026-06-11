<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ChatDotRound, EditPen, House, Notebook, Reading, UserFilled } from "@element-plus/icons-vue";
import CommunityView from "./components/CommunityView.vue";
import HomeView from "./components/HomeView.vue";
import MineView from "./components/MineView.vue";
import PublishView from "./components/PublishView.vue";
import RecordView from "./components/RecordView.vue";
import TutorialsView from "./components/TutorialsView.vue";
import { seedData } from "./data/seedData";
import { fetchCollection, fetchFishingRecords } from "./services/api";

const storageKeys = {
  records: "yuni_my_records",
  posts: "yuni_my_posts",
  favorites: "yuni_favorites"
};

function readStoredList(key) {
  try {
    const value = window.localStorage.getItem(key);
    const parsed = value ? JSON.parse(value) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function mergeById(primary, secondary) {
  const seen = new Set();
  return [...primary, ...secondary].filter((item) => {
    const id = item?.id || JSON.stringify(item);
    if (seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}

const tabs = [
  { id: "home", label: "首页", icon: House },
  { id: "community", label: "社区", icon: ChatDotRound },
  { id: "record", label: "记录", icon: Notebook },
  { id: "publish", label: "发布", icon: EditPen },
  { id: "tutorials", label: "技巧", icon: Reading },
  { id: "mine", label: "我的", icon: UserFilled }
];

const titles = {
  home: "FishMan",
  community: "钓友社区",
  record: "钓鱼记录",
  publish: "发布",
  tutorials: "钓鱼技巧",
  mine: "我的"
};

const activeTab = ref("home");
const toast = ref("");
let toastTimer;

const state = reactive({
  pois: seedData.pois,
  feed: seedData.feed,
  tutorials: seedData.tutorials,
  weather: seedData.weather,
  records: readStoredList(storageKeys.records),
  myPosts: readStoredList(storageKeys.posts),
  favorites: readStoredList(storageKeys.favorites)
});

const weatherText = computed(() => {
  const live = state.weather?.live || state.weather;
  if (!live) return "天气待更新";
  const direction = live.winddirection || live.wind_direction || "风向未知";
  const windLevel = live.windpower || live.wind_level;
  const temperature = live.temperature || live.temperature_c || live.feels_like_c || "";
  const wind = windLevel ? `${windLevel}级` : "";
  const pressure = live.pressure ? ` · ${live.pressure}hPa` : "";
  return `${live.weather} · ${temperature}℃ · ${direction} ${wind}${pressure}`;
});

const showTopActions = computed(() => activeTab.value !== "community");

function showToast(message) {
  toast.value = message;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    toast.value = "";
  }, 1800);
}

function addRecord(record) {
  if (record) {
    state.records.unshift(record);
  }
}

function addPost(post) {
  if (post) {
    state.myPosts.unshift(post);
    state.feed.unshift(post);
  }
}

function toggleFavorite(post) {
  if (!post) return;
  const index = state.favorites.findIndex((item) => item.id === post.id);
  if (index >= 0) {
    state.favorites.splice(index, 1);
    showToast(`已取消收藏：${post.title}`);
  } else {
    state.favorites.unshift(post);
    showToast(`已收藏：${post.title}`);
  }
}

function navigateTab(tabId) {
  activeTab.value = tabId;
}

async function searchPois(keyword) {
  const query = keyword ? `keyword=${encodeURIComponent(keyword)}` : "city=420100";
  state.pois = await fetchCollection(`/api/pois?${query}`, "pois");
  showToast(keyword ? `已搜索钓点：${keyword}` : "已刷新附近钓点");
}

async function loadInitialData() {
  const [pois, feed, tutorials, weather, records] = await Promise.all([
    fetchCollection("/api/pois?city=420100", "pois"),
    fetchCollection("/api/feed", "feed"),
    fetchCollection("/api/tutorials", "tutorials"),
    fetchCollection("/api/weather?city=420100", "weather"),
    fetchFishingRecords("demo_user")
  ]);
  state.pois = pois.length ? pois : seedData.pois;
  state.feed = feed.length ? feed : seedData.feed;
  state.feed = mergeById(state.myPosts, state.feed);
  state.tutorials = tutorials.length ? tutorials : seedData.tutorials;
  state.records = mergeById(state.records, records);
  if (weather && (weather.live || weather.forecast)) {
    state.weather = { ...seedData.weather, ...weather };
  }
}

onMounted(loadInitialData);

watch(
  () => state.records,
  (records) => {
    window.localStorage.setItem(storageKeys.records, JSON.stringify(records));
  },
  { deep: true }
);

watch(
  () => state.myPosts,
  (posts) => {
    window.localStorage.setItem(storageKeys.posts, JSON.stringify(posts));
  },
  { deep: true }
);

watch(
  () => state.favorites,
  (favorites) => {
    window.localStorage.setItem(storageKeys.favorites, JSON.stringify(favorites));
  },
  { deep: true }
);
</script>

<template>
  <main class="app-shell" :class="{ 'no-topbar': activeTab === 'community' }">
    <section v-if="activeTab !== 'community'" class="topbar">
      <div class="brand-block">
        <p v-if="activeTab === 'home'" class="eyebrow">GO · FISH · RECORD</p>
        <h1 :class="{ 'brand-title': activeTab === 'home' }">{{ titles[activeTab] }}</h1>
      </div>
      <div v-if="showTopActions" class="top-actions">
        <button class="icon-btn notification-btn" type="button" aria-label="消息" title="消息" @click="showToast('暂无新消息')">
          <el-icon><ChatDotRound /></el-icon>
          <span class="notification-dot"></span>
        </button>
      </div>
    </section>

    <section class="screen" :class="{ 'screen-flush': activeTab === 'community' }">
      <HomeView
        v-if="activeTab === 'home'"
        :pois="state.pois"
        :records="state.records"
        :weather="state.weather"
        :weather-text="weatherText"
        @action="showToast"
        @navigate="navigateTab"
        @search-pois="searchPois"
      />
      <CommunityView
        v-else-if="activeTab === 'community'"
        :feed="state.feed"
        :favorites="state.favorites"
        @action="showToast"
        @toggle-favorite="toggleFavorite"
      />
      <RecordView
        v-else-if="activeTab === 'record'"
        :weather="state.weather"
        :weather-text="weatherText"
        @action="showToast"
        @record-saved="addRecord"
      />
      <PublishView
        v-else-if="activeTab === 'publish'"
        :pois="state.pois"
        :records="state.records"
        @action="showToast"
        @submit-post="addPost"
      />
      <TutorialsView v-else-if="activeTab === 'tutorials'" :tutorials="state.tutorials" @action="showToast" />
      <MineView
        v-else
        :records="state.records"
        :posts="state.myPosts"
        :favorites="state.favorites"
        :feed="state.feed"
        @action="showToast"
        @toggle-favorite="toggleFavorite"
      />
    </section>

    <nav class="tabbar" aria-label="主导航">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="{ active: activeTab === tab.id }"
        class="tab"
        type="button"
        @click="activeTab = tab.id"
      >
        <span class="tab-icon"><el-icon><component :is="tab.icon" /></el-icon></span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </nav>

    <Transition name="toast">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </Transition>
  </main>
</template>
