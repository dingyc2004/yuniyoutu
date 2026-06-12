<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { ChatDotRound, Close, House, Notebook, Reading } from "@element-plus/icons-vue";
import CommunityView from "./components/CommunityView.vue";
import HomeView from "./components/HomeView.vue";
import MineView from "./components/MineView.vue";
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

const SEED_RECORDS = [
  {
    id: "seed_001",
    fishing_spot_name: "东湖听涛景区",
    location_name: "东湖听涛景区·南岸",
    fish_species: "鲫鱼",
    fish_count: 8,
    fish_weight: 3.6,
    fishing_method: "台钓",
    bait: "酒米+蚯蚓",
    start_time: "2026-05-18T05:40:00",
    created_at: "2026-05-18T05:40:00",
    duration_seconds: 14400,
    temperature: 23,
    weather: "晴",
    note: "清晨窗口期连杆，鲫鱼个头不错。东湖水位适中，岸边水草区鱼口密集。"
  },
  {
    id: "seed_002",
    fishing_spot_name: "青山江滩",
    location_name: "青山江滩·二七桥下",
    fish_species: "鲤鱼",
    fish_count: 3,
    fish_weight: 8.2,
    fishing_method: "野钓",
    bait: "玉米+商品饵",
    start_time: "2026-05-25T06:30:00",
    created_at: "2026-05-25T06:30:00",
    duration_seconds: 18000,
    temperature: 26,
    weather: "多云",
    note: "江水略浑，但大鲤鱼给力。其中一条接近5斤，遛鱼遛了十分钟。"
  },
  {
    id: "seed_003",
    fishing_spot_name: "东湖听涛景区",
    location_name: "东湖听涛景区·北码头",
    fish_species: "鳊鱼",
    fish_count: 5,
    fish_weight: 2.1,
    fishing_method: "台钓",
    bait: "商品饵(腥香)",
    start_time: "2026-06-02T05:00:00",
    created_at: "2026-06-02T05:00:00",
    duration_seconds: 10800,
    temperature: 24,
    weather: "晴",
    note: "北码头水位下降，改到深水区钓。鳊鱼连口，但个头偏小。"
  },
  {
    id: "seed_004",
    fishing_spot_name: "南湖",
    location_name: "南湖·西岸",
    fish_species: "草鱼",
    fish_count: 2,
    fish_weight: 7.5,
    fishing_method: "路亚",
    bait: "米诺",
    start_time: "2026-05-10T14:00:00",
    created_at: "2026-05-10T14:00:00",
    duration_seconds: 12600,
    temperature: 28,
    weather: "多云",
    note: "下午窗口期试了路亚，草鱼追饵很猛。第一条脱钩了，第二条稳稳上岸。"
  },
  {
    id: "seed_005",
    fishing_spot_name: "府河",
    location_name: "府河·盘龙城段",
    fish_species: "鲫鱼",
    fish_count: 12,
    fish_weight: 5.8,
    fishing_method: "野钓",
    bait: "酒米+红虫",
    start_time: "2026-04-28T06:00:00",
    created_at: "2026-04-28T06:00:00",
    duration_seconds: 21600,
    temperature: 20,
    weather: "阴",
    note: "春天的府河真好钓，鲫鱼抢食凶猛。十二尾里有一半都在半斤以上。"
  },
  {
    id: "seed_006",
    fishing_spot_name: "青山江滩",
    location_name: "青山江滩·天兴洲大桥",
    fish_species: "鳜鱼",
    fish_count: 2,
    fish_weight: 3.2,
    fishing_method: "路亚",
    bait: "软虫",
    start_time: "2026-06-05T05:20:00",
    created_at: "2026-06-05T05:20:00",
    duration_seconds: 10800,
    temperature: 25,
    weather: "晴",
    note: "早窗口用软虫搜结构区，两条鳜鱼都在石头缝附近咬的。路亚越来越顺手了。"
  },
  {
    id: "seed_007",
    fishing_spot_name: "东湖听涛景区",
    location_name: "东湖听涛景区·南岸",
    fish_species: "鲫鱼",
    fish_count: 6,
    fish_weight: 2.8,
    fishing_method: "台钓",
    bait: "酒米+麦粒",
    start_time: "2026-04-12T06:15:00",
    created_at: "2026-04-12T06:15:00",
    duration_seconds: 16200,
    temperature: 18,
    weather: "晴",
    note: "四月的东湖水温还偏低，鱼口比较轻。调灵漂后明显好转。"
  },
  {
    id: "seed_008",
    fishing_spot_name: "汤逊湖",
    location_name: "汤逊湖·南岸",
    fish_species: "鲢鱼",
    fish_count: 4,
    fish_weight: 11.0,
    fishing_method: "台钓",
    bait: "酸饵",
    start_time: "2026-05-31T07:00:00",
    created_at: "2026-05-31T07:00:00",
    duration_seconds: 19800,
    temperature: 27,
    weather: "多云",
    note: "汤逊湖的鲢鱼真大！四条加起来破十斤了。酸饵雾化要控制好，不然闹小鱼。"
  },
  {
    id: "seed_009",
    fishing_spot_name: "南湖",
    location_name: "南湖·东岸",
    fish_species: "鲤鱼",
    fish_count: 2,
    fish_weight: 4.6,
    fishing_method: "野钓",
    bait: "红薯+玉米",
    start_time: "2026-04-20T15:30:00",
    created_at: "2026-04-20T15:30:00",
    duration_seconds: 14400,
    temperature: 22,
    weather: "阴",
    note: "傍晚时分鲤鱼开始靠边，红薯饵效果不错。南湖水质比去年好了不少。"
  },
  {
    id: "seed_010",
    fishing_spot_name: "东湖听涛景区",
    location_name: "东湖听涛景区·南岸",
    fish_species: "鲫鱼",
    fish_count: 10,
    fish_weight: 4.5,
    fishing_method: "台钓",
    bait: "酒米+蚯蚓",
    start_time: "2026-06-08T05:30:00",
    created_at: "2026-06-08T05:30:00",
    duration_seconds: 12600,
    temperature: 26,
    weather: "晴",
    note: "最近几次出钓最舒服的一次。钓位选在芦苇丛边上，鲫鱼连杆不停。"
  }
];

const tabs = [
  { id: "home", label: "首页", icon: House },
  { id: "community", label: "社区", icon: ChatDotRound },
  { id: "record", label: "记录", icon: Notebook },
  { id: "tutorials", label: "技巧", icon: Reading }
];

const titles = {
  home: "FishMan",
  community: "钓友社区",
  record: "钓鱼记录",
  tutorials: "钓鱼技巧",
  mine: "我的"
};

const activeTab = ref("home");
const showMineDrawer = ref(false);
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
  state.records = mergeById(state.records, SEED_RECORDS);
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
        :pois="state.pois"
        :records="state.records"
        @action="showToast"
        @toggle-favorite="toggleFavorite"
        @submit-post="addPost"
      />
      <RecordView
        v-else-if="activeTab === 'record'"
        :weather="state.weather"
        :weather-text="weatherText"
        @action="showToast"
        @record-saved="addRecord"
      />
      <TutorialsView v-else :tutorials="state.tutorials" @action="showToast" />
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
              :records="state.records"
              :posts="state.myPosts"
              :favorites="state.favorites"
              :feed="state.feed"
              @action="showToast"
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
