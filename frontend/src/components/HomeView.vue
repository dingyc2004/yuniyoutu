<script setup>
import { computed, ref } from "vue";
import {
  ArrowLeft,
  ArrowRight,
  ChatDotRound,
  Compass,
  DataAnalysis,
  Notebook,
  Reading,
  Search,
  Share,
  Star,
  Sunny,
  TrendCharts,
  VideoPlay
} from "@element-plus/icons-vue";

const props = defineProps({
  feed: { type: Array, default: () => [] },
  weatherText: { type: String, default: "天气待更新" }
});

const emit = defineEmits(["action", "navigate"]);
const query = ref("");
const activeChannel = ref("推荐");
const hotRail = ref(null);
const activeHotIndex = ref(0);
const selectedPost = ref(null);
const channels = ["推荐", "同城", "路亚", "新手", "热点", "关注"];
const weatherTemperature = computed(() => props.weatherText.match(/-?\d+(?:\.\d+)?(?=℃)/)?.[0] || "--");

const hotItems = computed(() =>
  [...props.feed]
    .sort((a, b) => (b.likes || 0) - (a.likes || 0))
    .slice(0, 4)
);

const shownFeed = computed(() => {
  const text = query.value.trim();
  return props.feed.filter((item) => {
    const haystack = `${item.title} ${item.excerpt} ${item.meta} ${(item.tags || []).join(" ")}`;
    const channelOk =
      activeChannel.value === "推荐" ||
      activeChannel.value === "热点" && item.likes >= 100 ||
      activeChannel.value === "关注" && ["post_001", "post_002"].includes(item.id) ||
      haystack.includes(activeChannel.value);
    return channelOk && (!text || haystack.includes(text));
  });
});

function submitSearch() {
  emit("action", query.value.trim() ? `搜索内容：${query.value.trim()}` : "看看今天的热门钓获");
}

function showHot(index) {
  const total = hotItems.value.length;
  if (!total) return;
  activeHotIndex.value = (index + total) % total;
  const rail = hotRail.value;
  if (rail) {
    rail.scrollTo({
      left: activeHotIndex.value * rail.clientWidth,
      behavior: "smooth"
    });
  }
}

function syncHotIndex() {
  const rail = hotRail.value;
  if (!rail) return;
  activeHotIndex.value = Math.round(rail.scrollLeft / rail.clientWidth);
}

function openPost(post) {
  selectedPost.value = post;
}

function closePost() {
  selectedPost.value = null;
}

function postImages(post) {
  const count = post.imageCount || (post.format === "图文" ? 3 : 1);
  return Array.from({ length: count }, (_, index) => ({
    id: `${post.id}-image-${index}`,
    tone: ["blue", "green", "amber", "purple"][index % 4]
  }));
}
</script>

<template>
  <section v-if="!selectedPost" class="home-view">
    <section class="weather-dashboard">
      <div class="weather-main">
        <div>
          <div class="weather-location">
            <strong>武汉 · 东湖</strong>
            <span>适宜垂钓</span>
          </div>
          <div class="temperature-line">
            <strong>{{ weatherTemperature }}<small>℃</small></strong>
            <span class="weather-symbol"><el-icon><Sunny /></el-icon></span>
          </div>
          <p>{{ weatherText }}</p>
        </div>
        <div class="fishing-index" aria-label="适钓指数 82">
          <div class="index-ring"><strong>82</strong></div>
          <span>适钓指数</span>
        </div>
      </div>
    </section>

    <section class="daily-recommend">
      <div class="section-head">
        <h2>今日推荐</h2>
        <el-button text class="text-link" :icon="ArrowRight" @click="emit('navigate', 'fish')">更多</el-button>
      </div>
      <button class="recommend-card tone-blue" type="button" @click="emit('navigate', 'fish')">
        <span class="recommend-label">翘嘴活跃期</span>
        <strong>清晨窗口 06:30-09:00</strong>
        <small>东湖沿岸 · 距离 2.1km · 鱼口良好</small>
        <span class="fish-silhouette">FISH</span>
      </button>
    </section>

    <section class="feature-grid" aria-label="快捷功能">
      <button type="button" @click="emit('navigate', 'fish')"><span><el-icon><Compass /></el-icon></span><strong>钓点探索</strong></button>
      <button type="button" @click="emit('action', '已打开潮汐天气')"><span><el-icon><Sunny /></el-icon></span><strong>潮汐天气</strong></button>
      <button type="button" @click="emit('action', '已打开鱼情预测')"><span><el-icon><TrendCharts /></el-icon></span><strong>鱼情预测</strong></button>
      <button type="button" @click="emit('navigate', 'record')"><span><el-icon><Notebook /></el-icon></span><strong>钓鱼日记</strong></button>
      <button type="button" @click="emit('navigate', 'tutorials')"><span><el-icon><Reading /></el-icon></span><strong>技巧百科</strong></button>
    </section>

    <form class="home-search" @submit.prevent="submitSearch">
      <el-icon aria-hidden="true"><Search /></el-icon>
      <el-input v-model="query" type="search" placeholder="搜索钓点、鱼种、教程、装备" clearable />
      <el-button native-type="submit" type="primary" round>搜索</el-button>
    </form>

    <el-segmented v-model="activeChannel" class="home-channels" :options="channels" aria-label="内容频道" />

    <section class="hot-zone section" aria-label="热点视频资讯">
      <div class="section-head home-feed-head">
        <div><h2>钓友动态</h2></div>
        <span class="meta">实时更新</span>
      </div>
      <button class="hot-nav previous" type="button" aria-label="上一个热点" @click="showHot(activeHotIndex - 1)">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <div ref="hotRail" class="hot-rail" @scroll.passive="syncHotIndex">
        <article
          v-for="(item, index) in hotItems"
          :key="item.id"
          class="hot-card"
          @click="openPost(item)"
        >
          <div :class="['hot-cover', `tone-${item.coverTone || 'green'}`]">
            <span class="hot-rank">TOP {{ index + 1 }}</span>
          </div>
          <div class="hot-info">
            <strong>{{ item.title }}</strong>
            <p>{{ item.meta }}</p>
          </div>
        </article>
      </div>
      <button class="hot-nav next" type="button" aria-label="下一个热点" @click="showHot(activeHotIndex + 1)">
        <el-icon><ArrowRight /></el-icon>
      </button>
      <div class="hot-dots" aria-label="热点位置">
        <button
          v-for="(_, index) in hotItems"
          :key="index"
          :class="{ active: activeHotIndex === index }"
          type="button"
          :aria-label="`切换到第 ${index + 1} 个热点`"
          @click="showHot(index)"
        ></button>
      </div>
    </section>

    <section class="home-quick">
      <button type="button" @click="emit('action', '已进入钓点热力榜')">
        <strong>钓点热力</strong>
        <span>{{ weatherText }}</span>
      </button>
      <button type="button" @click="emit('action', '已打开今日鱼口')">
        <strong>今日鱼口</strong>
        <span>风向、气压、窗口期</span>
      </button>
    </section>

    <section class="video-grid" aria-label="推荐视频">
      <article
        v-for="post in shownFeed"
        :key="post.id"
        class="video-tile"
        @click="openPost(post)"
      >
        <div :class="['video-cover', `tone-${post.coverTone || 'green'}`]">
          <span class="video-format">{{ post.format }}</span>
          <span class="play-dot"><el-icon><VideoPlay /></el-icon></span>
        </div>
        <h3>{{ post.title }}</h3>
        <p>{{ post.author }} · {{ post.likes }}赞</p>
      </article>
    </section>
  </section>

  <section v-else-if="selectedPost.format === '视频'" class="short-video-page">
    <button class="video-back" type="button" aria-label="返回" @click="closePost"><el-icon><ArrowLeft /></el-icon></button>
    <div :class="['short-video-stage', `tone-${selectedPost.coverTone || 'blue'}`]">
      <div class="short-video-copy">
        <strong>{{ selectedPost.title }}</strong>
        <p>@{{ selectedPost.author }} · {{ selectedPost.meta }}</p>
      </div>
      <div class="short-video-actions">
        <button type="button" @click="emit('action', `喜欢：${selectedPost.title}`)"><el-icon><DataAnalysis /></el-icon><span>{{ selectedPost.likes }}</span></button>
        <button type="button" @click="emit('action', `评论：${selectedPost.title}`)"><el-icon><ChatDotRound /></el-icon><span>{{ selectedPost.comments }}</span></button>
        <button type="button" @click="emit('action', `收藏：${selectedPost.title}`)"><el-icon><Star /></el-icon><span>{{ selectedPost.saves }}</span></button>
        <button type="button" @click="emit('action', `分享：${selectedPost.title}`)"><el-icon><Share /></el-icon><span>分享</span></button>
      </div>
    </div>
  </section>

  <section v-else class="post-detail-page">
    <el-button text class="back-link" :icon="ArrowLeft" @click="closePost">返回首页</el-button>
    <div class="post-image-rail">
      <div
        v-for="image in postImages(selectedPost)"
        :key="image.id"
        :class="['post-image', `tone-${image.tone}`]"
      >
        <span>{{ selectedPost.author }}</span>
      </div>
    </div>
    <article class="post-detail-body">
      <div class="author-row">
        <el-avatar :size="38">{{ selectedPost.avatar }}</el-avatar>
        <div>
          <strong>{{ selectedPost.author }}</strong>
          <p class="meta">{{ selectedPost.meta }}</p>
        </div>
      </div>
      <h2>{{ selectedPost.title }}</h2>
      <p class="spot-copy">{{ selectedPost.excerpt }}</p>
      <div class="chips compact">
        <el-tag v-for="tag in selectedPost.tags" :key="tag" round type="primary" effect="light">{{ tag }}</el-tag>
      </div>

      <section class="detail-section">
        <h4>评论区</h4>
        <div class="comment-list">
          <div class="comment-item">
            <strong>武汉钓友 008</strong>
            <p>这个窗口期很有参考价值，准备周末照着试一次。</p>
          </div>
          <div class="comment-item">
            <strong>青山探点</strong>
            <p>同城钓友确认，最近水位变化比较明显，注意安全。</p>
          </div>
        </div>
      </section>
    </article>
  </section>
</template>
