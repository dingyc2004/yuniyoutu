<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ChatDotRound, Close, Goods, House, Notebook, Reading } from "@element-plus/icons-vue";
import CommunityView from "./components/CommunityView.vue";
import HomeView from "./components/HomeView.vue";
import MineView from "./components/MineView.vue";
import RecordView from "./components/RecordView.vue";
import ServicesView from "./components/ServicesView.vue";
import TutorialsView from "./components/TutorialsView.vue";
import { seedData } from "./data/seedData";
import { fetchCollection, fetchFishingRecords, fetchUser, fetchUserMembership } from "./services/api";

const DEMO_MEMBER_ID = "demo_user";
const DEMO_NONMEMBER_ID = "demo_nonmember";
const currentUserId = ref(DEMO_MEMBER_ID);
const demoMode = ref("member"); // "member" | "nonmember"

const storageKeys = {
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
  { id: "tutorials", label: "技巧", icon: Reading },
  { id: "services", label: "服务", icon: Goods }
];

const titles = {
  home: "FishMan",
  community: "钓友社区",
  record: "钓鱼记录",
  tutorials: "钓鱼技巧",
  services: "活动与装备",
  mine: "我的"
};

const activeTab = ref("home");
const showMineDrawer = ref(false);
const toast = ref("");
const openMessagesToken = ref(0);
const pendingShareRecord = ref(null);
let toastTimer;

const state = reactive({
  pois: seedData.pois,
  feed: seedData.feed,
  tutorials: seedData.tutorials,
  weather: seedData.weather,
  records: [],
  myPosts: readStoredList(storageKeys.posts),
  favorites: readStoredList(storageKeys.favorites),
  user: null,
  membership: null,
  notifications: []
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

function openMessages() {
  activeTab.value = "community";
  openMessagesToken.value += 1;
}

function shareRecord(record) {
  pendingShareRecord.value = record;
  activeTab.value = "community";
  showToast("已带入本次鱼获，可补充内容后发布");
}

async function searchPois(keyword) {
  const query = keyword ? `keyword=${encodeURIComponent(keyword)}` : "city=420100";
  state.pois = await fetchCollection(`/api/pois?${query}`, "pois");
  showToast(keyword ? `已搜索钓点：${keyword}` : "已刷新附近钓点");
}

async function loadInitialData() {
  const [pois, feed, tutorials, weather] = await Promise.all([
    fetchCollection("/api/pois?city=420100", "pois"),
    fetchCollection("/api/feed", "feed"),
    fetchCollection("/api/tutorials", "tutorials"),
    fetchCollection("/api/weather?city=420100", "weather")
  ]);
  state.pois = pois.length ? pois : seedData.pois;
  state.feed = feed.length ? feed : seedData.feed;
  state.feed = mergeById(state.myPosts, state.feed);
  state.tutorials = tutorials.length ? tutorials : seedData.tutorials;
  if (weather && (weather.live || weather.forecast)) {
    state.weather = { ...seedData.weather, ...weather };
  }
  await loadUserData();
}

async function loadUserData() {
  const uid = currentUserId.value;
  const [records, user, membership, notifications] = await Promise.all([
    fetchFishingRecords(uid),
    fetchUser(uid),
    fetchUserMembership(uid),
    fetchCollection(`/api/users/${encodeURIComponent(uid)}/notifications`, null)
  ]);
  state.records = records;
  state.user = user;
  state.membership = membership;
  state.notifications = Array.isArray(notifications) ? notifications : [];
}

async function switchDemoMode(mode) {
  demoMode.value = mode;
  currentUserId.value = mode === "member" ? DEMO_MEMBER_ID : DEMO_NONMEMBER_ID;
  showToast(mode === "member" ? "已切换到会员演示" : "已切换到非会员演示");
  await loadUserData();
}

onMounted(loadInitialData);

watch(
  () => state.records,
  (records) => {
    window.localStorage.setItem("yuni_my_records", JSON.stringify(records));
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
  <main
    class="app-shell"
    :class="{
      'no-topbar': activeTab === 'community',
      'home-shell': activeTab === 'home'
    }"
  >
    <section class="topbar" :class="{ 'topbar-mini': activeTab === 'community' }">
      <button class="hamburger-btn" type="button" aria-label="我的" @click="showMineDrawer = true">
        <span class="ham-line"></span>
        <span class="ham-line"></span>
        <span class="ham-line"></span>
      </button>
      <div v-if="activeTab !== 'community'" class="brand-block">
        <p v-if="activeTab === 'home'" class="eyebrow">GO · FISH · RECORD</p>
        <h1 :class="{ 'brand-title': activeTab === 'home' }">{{ titles[activeTab] }}</h1>
      </div>
      <div v-if="showTopActions && activeTab !== 'community'" class="top-actions">
        <button
          class="icon-btn demo-toggle-btn"
          :class="{ active: demoMode === 'nonmember' }"
          type="button"
          :title="demoMode === 'member' ? '当前：会员演示 · 点击切换非会员' : '当前：非会员演示 · 点击切换会员'"
          @click="switchDemoMode(demoMode === 'member' ? 'nonmember' : 'member')"
        >
          {{ demoMode === 'member' ? 'VIP' : '体验' }}
        </button>
        <button class="icon-btn notification-btn" type="button" aria-label="消息" title="消息" @click="openMessages">
          <el-icon><ChatDotRound /></el-icon>
          <span class="notification-dot"></span>
          <b v-if="state.notifications.length" class="notification-count">{{ state.notifications.length }}</b>
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
        :current-user-id="currentUserId"
        :open-messages-token="openMessagesToken"
        :share-record="pendingShareRecord"
        :feed="state.feed"
        :favorites="state.favorites"
        :pois="state.pois"
        :records="state.records"
        @action="showToast"
        @toggle-favorite="toggleFavorite"
        @submit-post="addPost"
        @share-consumed="pendingShareRecord = null"
      />
      <RecordView
        v-else-if="activeTab === 'record'"
        :current-user-id="currentUserId"
        :weather="state.weather"
        :weather-text="weatherText"
        @action="showToast"
        @record-saved="addRecord"
        @share-record="shareRecord"
      />
      <TutorialsView
        v-else-if="activeTab === 'tutorials'"
        :current-user-id="currentUserId"
        :tutorials="state.tutorials"
        @action="showToast"
      />
      <ServicesView
        v-else
        :current-user-id="currentUserId"
        @action="showToast"
        @open-chat="openMessages"
        @record-created="addRecord"
      />
    </section>

    <Transition name="drawer">
      <div v-if="showMineDrawer" class="mine-drawer-overlay" @click.self="showMineDrawer = false">
        <aside class="mine-drawer">
          <header class="mine-drawer-head">
            <h2>我的</h2>
            <button class="drawer-close-btn" type="button" aria-label="关闭" @click="showMineDrawer = false">
              <el-icon><Close /></el-icon>
            </button>
          </header>
          <div class="mine-drawer-body">
            <MineView
              :current-user-id="currentUserId"
              :records="state.records"
              :posts="state.myPosts"
              :favorites="state.favorites"
              :feed="state.feed"
              :user="state.user"
              :membership="state.membership"
              @action="showToast"
              @navigate="(tab) => { showMineDrawer = false; activeTab = tab; }"
              @toggle-favorite="toggleFavorite"
            />
          </div>
        </aside>
      </div>
    </Transition>

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
