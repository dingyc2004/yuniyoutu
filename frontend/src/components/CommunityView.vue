<script setup>
import { computed, ref } from "vue";
import {
  ArrowLeft,
  Bell,
  ChatDotRound,
  Collection,
  Search,
  Share,
  Star
} from "@element-plus/icons-vue";

const props = defineProps({
  feed: { type: Array, default: () => [] }
});

const emit = defineEmits(["action"]);

const query = ref("");
const activeChannel = ref("推荐");
const selectedPost = ref(null);
const following = ref(new Set());

const channels = ["推荐", "同城", "关注", "路亚", "台钓", "野钓", "海钓", "新手"];

const feedItems = computed(() => (Array.isArray(props.feed) ? props.feed.map(normalizePost) : []));

const shownFeed = computed(() => {
  const text = query.value.trim().toLowerCase();
  const matched = feedItems.value.filter((item) => {
    const haystack = item.searchText;
    const channelOk =
      activeChannel.value === "推荐" ||
      (activeChannel.value === "关注" && ["post_001", "post_002", "post_006"].includes(item.id)) ||
      (activeChannel.value === "同城" && /武汉|东湖|青山|南湖/.test(haystack)) ||
      (activeChannel.value === "新手" && /新手|入门|第一条/.test(haystack)) ||
      haystack.includes(activeChannel.value.toLowerCase());
    return channelOk && (!text || haystack.includes(text));
  });
  if (matched.length || text) return matched;
  return activeChannel.value === "推荐" ? [] : feedItems.value;
});

const leftColumn = computed(() => shownFeed.value.filter((_, i) => i % 2 === 0));
const rightColumn = computed(() => shownFeed.value.filter((_, i) => i % 2 === 1));

function openPost(post) {
  selectedPost.value = post;
}

function closePost() {
  selectedPost.value = null;
}

function submitSearch() {
  emit("action", query.value.trim() ? `搜索：${query.value.trim()}` : "输入关键词搜索社区内容");
}

function normalizePost(item) {
  const tags = Array.isArray(item?.tags)
    ? item.tags
    : String(item?.tags || "")
      .split(/[,\s]+/)
      .filter(Boolean);
  const postType = item?.postType || item?.post_type || item?.type || "";
  const publishedAt = item?.publishedAt || formatPublishedAt(item?.created_at);
  const excerpt = item?.excerpt || item?.content || "这位钓友还没有补充正文。";
  const normalized = {
    ...item,
    id: item?.id || `post_${Math.random().toString(36).slice(2)}`,
    title: item?.title || "钓友动态",
    excerpt,
    meta: item?.meta || item?.location_text || postType || "社区动态",
    postType,
    tags,
    author: item?.author || "钓友",
    avatar: item?.avatar || "钓",
    likes: Number(item?.likes || 0),
    comments: Number(item?.comments || 0),
    saves: Number(item?.saves || 0),
    format: item?.format || "图文",
    coverTone: item?.coverTone || item?.cover_tone || "blue",
    imageCount: item?.imageCount || item?.image_count || item?.images?.length || 1,
    publishedAt
  };
  normalized.searchText = [
    normalized.title,
    normalized.excerpt,
    normalized.meta,
    normalized.postType,
    normalized.author,
    ...normalized.tags
  ].join(" ").toLowerCase();
  return normalized;
}

function formatPublishedAt(value) {
  if (!value) return "刚刚";
  const timestamp = new Date(value).getTime();
  if (!Number.isFinite(timestamp)) return "刚刚";
  const hours = Math.max(1, Math.round((Date.now() - timestamp) / 36e5));
  if (hours < 24) return `${hours}小时前`;
  const days = Math.round(hours / 24);
  return days <= 1 ? "昨天" : `${days}天前`;
}

function toggleFollow(author) {
  const next = new Set(following.value);
  if (next.has(author)) {
    next.delete(author);
    emit("action", `已取消关注 ${author}`);
  } else {
    next.add(author);
    emit("action", `已关注 ${author}`);
  }
  following.value = next;
}

function postImages(post) {
  const count = post.imageCount || (post.format === "图文" ? 3 : 1);
  return Array.from({ length: count }, (_, index) => ({
    id: `${post.id}-image-${index}`,
    tone: ["sand", "mist", "clay", "stone"][index % 4]
  }));
}

function coverAspect(post) {
  const seed = (post.id || "").length + (post.imageCount || 1);
  const ratios = ["tall", "medium", "short"];
  return ratios[seed % ratios.length];
}
</script>

<template>
  <section v-if="selectedPost" class="community-page community-detail">
    <header class="community-detail-head">
      <el-button text class="back-link" :icon="ArrowLeft" @click="closePost">返回社区</el-button>
    </header>

    <div class="community-detail-images">
      <div
        v-for="image in postImages(selectedPost)"
        :key="image.id"
        :class="['community-detail-image', `cover-${image.tone}`]"
      ></div>
    </div>

    <article class="community-detail-body">
      <div class="community-detail-author">
        <el-avatar :size="40">{{ selectedPost.avatar }}</el-avatar>
        <div class="community-detail-author-copy">
          <strong>{{ selectedPost.author }}</strong>
          <p class="meta">{{ selectedPost.publishedAt || "刚刚" }} · {{ selectedPost.postType || selectedPost.format }}</p>
        </div>
        <el-button
          round
          size="small"
          :type="following.has(selectedPost.author) ? 'default' : 'primary'"
          plain
          @click="toggleFollow(selectedPost.author)"
        >
          {{ following.has(selectedPost.author) ? "已关注" : "关注" }}
        </el-button>
      </div>

      <h1>{{ selectedPost.title }}</h1>
      <p class="community-detail-text">{{ selectedPost.excerpt }}</p>

      <div class="chips compact">
        <el-tag v-for="tag in selectedPost.tags" :key="tag" round effect="light" size="small">{{ tag }}</el-tag>
      </div>

      <div class="community-detail-actions">
        <button type="button" @click="emit('action', `点赞：${selectedPost.title}`)">
          <el-icon><Star /></el-icon>{{ selectedPost.likes }}
        </button>
        <button type="button" @click="emit('action', `收藏：${selectedPost.title}`)">
          <el-icon><Collection /></el-icon>{{ selectedPost.saves }}
        </button>
        <button type="button" @click="emit('action', `分享：${selectedPost.title}`)">
          <el-icon><Share /></el-icon>分享
        </button>
      </div>

      <section class="detail-section">
        <h4>评论 · {{ selectedPost.comments }}</h4>
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
        <el-button class="community-comment-btn" round plain @click="emit('action', '写下你的看法')">
          <el-icon><ChatDotRound /></el-icon>
          写评论
        </el-button>
      </section>
    </article>
  </section>

  <section v-else class="community-page">
    <header class="community-topbar">
      <form class="community-search" @submit.prevent="submitSearch">
        <el-icon aria-hidden="true"><Search /></el-icon>
        <input v-model="query" type="search" placeholder="搜索钓点、鱼种、技巧、用户" />
      </form>
      <button type="button" class="community-msg-btn" aria-label="消息" @click="emit('action', '暂无新消息')">
        <el-icon><Bell /></el-icon>
      </button>
    </header>

    <nav class="community-channels" aria-label="社区频道">
      <button
        v-for="channel in channels"
        :key="channel"
        type="button"
        :class="{ active: activeChannel === channel }"
        @click="activeChannel = channel"
      >
        {{ channel }}
      </button>
    </nav>

    <div v-if="!shownFeed.length" class="community-empty card">
      <p>暂无匹配内容</p>
      <span class="meta">换个频道或搜索词试试</span>
    </div>

    <div v-else class="community-masonry" aria-label="社区内容流">
      <div class="community-column">
        <article
          v-for="post in leftColumn"
          :key="post.id"
          class="community-card"
          role="button"
          tabindex="0"
          @click="openPost(post)"
          @keydown.enter.prevent="openPost(post)"
        >
          <div :class="['community-card-cover', `ratio-${coverAspect(post)}`, `cover-${post.coverTone || 'sand'}`]">
            <span v-if="post.format === '视频'" class="community-card-badge">视频</span>
            <span v-if="post.postType" class="community-card-type">{{ post.postType }}</span>
          </div>
          <div class="community-card-body">
            <h3>{{ post.title }}</h3>
            <div class="community-card-foot">
              <div class="community-card-author">
                <el-avatar :size="22">{{ post.avatar }}</el-avatar>
                <span>{{ post.author }}</span>
              </div>
              <span class="community-card-like">
                <el-icon><Star /></el-icon>
                {{ post.likes }}
              </span>
            </div>
            <p class="community-card-time">{{ post.publishedAt || "刚刚" }}</p>
          </div>
        </article>
      </div>
      <div class="community-column">
        <article
          v-for="post in rightColumn"
          :key="post.id"
          class="community-card"
          role="button"
          tabindex="0"
          @click="openPost(post)"
          @keydown.enter.prevent="openPost(post)"
        >
          <div :class="['community-card-cover', `ratio-${coverAspect(post)}`, `cover-${post.coverTone || 'mist'}`]">
            <span v-if="post.format === '视频'" class="community-card-badge">视频</span>
            <span v-if="post.postType" class="community-card-type">{{ post.postType }}</span>
          </div>
          <div class="community-card-body">
            <h3>{{ post.title }}</h3>
            <div class="community-card-foot">
              <div class="community-card-author">
                <el-avatar :size="22">{{ post.avatar }}</el-avatar>
                <span>{{ post.author }}</span>
              </div>
              <span class="community-card-like">
                <el-icon><Star /></el-icon>
                {{ post.likes }}
              </span>
            </div>
            <p class="community-card-time">{{ post.publishedAt || "刚刚" }}</p>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
