<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import {
  Bell,
  Compass,
  EditPen,
  House,
  Notebook,
  Plus,
  Reading,
  UserFilled
} from "@element-plus/icons-vue";
import FishingView from "./components/FishingView.vue";
import HomeView from "./components/HomeView.vue";
import MineView from "./components/MineView.vue";
import PublishView from "./components/PublishView.vue";
import RecordView from "./components/RecordView.vue";
import TutorialsView from "./components/TutorialsView.vue";
import { seedData } from "./data/seedData";
import { fetchCollection } from "./services/api";

const tabs = [
  { id: "home", label: "首页", icon: House },
  { id: "fish", label: "探索", icon: Compass },
  { id: "record", label: "日记", icon: Notebook },
  { id: "publish", label: "发布", icon: EditPen },
  { id: "tutorials", label: "技巧", icon: Reading },
  { id: "mine", label: "我的", icon: UserFilled }
];

const titles = {
  home: "FISH ON!",
  fish: "钓点探索",
  record: "钓鱼日记",
  publish: "记一竿",
  tutorials: "钓鱼教程",
  mine: "我的战绩"
};

const activeTab = ref("home");
const toast = ref("");
let toastTimer;

const state = reactive({
  pois: seedData.pois,
  feed: seedData.feed,
  tutorials: seedData.tutorials,
  weather: seedData.weather,
  records: [],
  myPosts: []
});

const weatherText = computed(() => {
  const live = state.weather?.live || state.weather;
  if (!live) return "天气待更新";
  const direction = live.winddirection || live.wind_direction || "风向未知";
  const windLevel = live.windpower || live.wind_level;
  const temperature = live.temperature || live.temperature_c || live.feels_like_c || "";
  const wind = windLevel ? `${windLevel}级` : "";
  return `${live.weather} · ${temperature}℃ · ${direction} ${wind}`;
});

function showToast(message) {
  toast.value = message;
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    toast.value = "";
  }, 1800);
}

function addPost(post) {
  state.myPosts.unshift(post);
  state.feed.unshift(post);
}

function addRecord(record) {
  if (record) {
    state.records.unshift(record);
  }
}

async function searchPois(keyword) {
  const query = keyword ? `keyword=${encodeURIComponent(keyword)}` : "city=420100";
  state.pois = await fetchCollection(`/api/pois?${query}`, "pois");
  showToast(keyword ? `已搜索：${keyword}` : "已刷新附近钓点");
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
      <div class="brand-block">
        <p v-if="activeTab === 'home'" class="eyebrow">EXPLORE · RECORD · ENJOY</p>
        <h1 :class="{ 'brand-title': activeTab === 'home' }">{{ titles[activeTab] }}</h1>
      </div>
      <div class="top-actions">
        <button class="icon-btn notification-btn" type="button" aria-label="消息" title="消息" @click="showToast('暂无新消息')">
          <el-icon><Bell /></el-icon>
          <span class="notification-dot"></span>
        </button>
        <button class="icon-btn" type="button" aria-label="快捷发布" title="快捷发布" @click="activeTab = 'publish'">
          <el-icon><Plus /></el-icon>
        </button>
      </div>
    </section>

    <section class="screen">
      <HomeView
        v-if="activeTab === 'home'"
        :feed="state.feed"
        :weather-text="weatherText"
        @action="showToast"
        @navigate="activeTab = $event"
      />
      <FishingView
        v-else-if="activeTab === 'fish'"
        :pois="state.pois"
        :weather-text="weatherText"
        @search="searchPois"
        @action="showToast"
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
        @action="showToast"
        @submit-post="addPost"
      />
      <TutorialsView v-else-if="activeTab === 'tutorials'" :tutorials="state.tutorials" @action="showToast" />
      <MineView v-else :posts="state.myPosts" />
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
