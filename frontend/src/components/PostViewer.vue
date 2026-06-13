<script setup>
import { computed, ref, watch } from "vue";
import {
  ArrowLeft,
  CaretBottom,
  CaretTop,
  ChatDotRound,
  Collection,
  Share,
  Star,
  VideoPlay
} from "@element-plus/icons-vue";

const props = defineProps({
  post: { type: Object, required: true },
  feed: { type: Array, default: () => [] },
  favorites: { type: Array, default: () => [] },
  backLabel: { type: String, default: "返回" }
});

const emit = defineEmits(["back", "action", "toggle-favorite", "open-author"]);

const liked = ref(false);
const commentText = ref("");
const currentVideoIndex = ref(0);

const normalizedFeed = computed(() => {
  const items = Array.isArray(props.feed) && props.feed.length ? props.feed : [props.post];
  return items.map(normalizePost);
});

const videos = computed(() => {
  const items = normalizedFeed.value.filter((item) => item.format === "视频");
  const current = normalizePost(props.post);
  if (current.format !== "视频") return items;
  return items.some((item) => item.id === current.id) ? items : [current, ...items];
});

const currentPost = computed(() => {
  if (isVideoPost.value) return videos.value[currentVideoIndex.value] || normalizePost(props.post);
  return normalizePost(props.post);
});

const isVideoPost = computed(() => normalizePost(props.post).format === "视频");
const isFavorited = computed(() => props.favorites.some((item) => item.id === currentPost.value.id));
const likeCount = computed(() => Number(currentPost.value.likes || 0) + (liked.value ? 1 : 0));
const saveCount = computed(() => Number(currentPost.value.saves || 0) + (isFavorited.value ? 1 : 0));
const comments = computed(() => [
  {
    id: "c1",
    author: "武汉钓友 008",
    text: currentPost.value.format === "视频" ? "这段上鱼节奏很清楚，适合复盘窗口期。" : "这个窗口期很有参考价值，准备周末照着试一次。"
  },
  {
    id: "c2",
    author: "青山探点",
    text: "同城钓友确认，最近水位变化比较明显，注意安全。"
  }
]);

watch(
  () => props.post?.id,
  () => {
    liked.value = false;
    const index = videos.value.findIndex((item) => item.id === props.post?.id);
    currentVideoIndex.value = Math.max(0, index);
  },
  { immediate: true }
);

function normalizePost(item) {
  const tags = Array.isArray(item?.tags)
    ? item.tags
    : String(item?.tags || "")
      .split(/[,\s]+/)
      .filter(Boolean);
  const content = item?.content || item?.excerpt || item?.note || "这位钓友还没有补充正文。";
  return {
    ...item,
    id: item?.id || `post_${Math.random().toString(36).slice(2)}`,
    format: item?.format || "图文",
    title: item?.title || "钓友动态",
    author: item?.author || "钓友",
    avatar: item?.avatar || "钓",
    excerpt: content,
    content,
    meta: item?.meta || item?.location_text || item?.postType || item?.post_type || "社区动态",
    postType: item?.postType || item?.post_type || "鱼获分享",
    tags,
    likes: Number(item?.likes || 0),
    comments: Number(item?.comments || 0),
    saves: Number(item?.saves || 0),
    coverTone: item?.coverTone || item?.cover_tone || "blue",
    imageCount: item?.imageCount || item?.image_count || item?.images?.length || 1,
    publishedAt: item?.publishedAt || formatPublishedAt(item?.created_at)
  };
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

function postImages(post) {
  const count = post.imageCount || (post.format === "图文" ? 3 : 1);
  return Array.from({ length: count }, (_, index) => ({
    id: `${post.id}-image-${index}`,
    tone: ["sand", "mist", "clay", "stone"][index % 4]
  }));
}

function toggleLike() {
  liked.value = !liked.value;
  emit("action", `${liked.value ? "已点赞" : "已取消点赞"}：${currentPost.value.title}`);
}

function toggleFavorite() {
  emit("toggle-favorite", currentPost.value);
}

function submitComment() {
  const text = commentText.value.trim();
  emit("action", text ? `已评论：${text}` : "写下你的看法");
  commentText.value = "";
}

function switchVideo(direction) {
  if (!videos.value.length) return;
  const next = currentVideoIndex.value + direction;
  currentVideoIndex.value = Math.min(videos.value.length - 1, Math.max(0, next));
}
</script>

<template>
  <section v-if="isVideoPost" class="short-video-page">
    <button class="video-back" type="button" :aria-label="backLabel" @click="emit('back')">
      <el-icon><ArrowLeft /></el-icon>
    </button>

    <section :class="['short-video-stage', `cover-${currentPost.coverTone}`]">
      <div class="short-video-play">
        <el-icon><VideoPlay /></el-icon>
      </div>
      <div class="short-video-copy">
        <button type="button" class="short-video-author" @click="emit('open-author', currentPost)">@{{ currentPost.author }}</button>
        <strong>{{ currentPost.title }}</strong>
        <p>{{ currentPost.excerpt }}</p>
        <div class="short-video-tags">
          <span v-for="tag in currentPost.tags.slice(0, 3)" :key="tag">{{ tag }}</span>
        </div>
      </div>
      <div class="short-video-actions">
        <button type="button" :class="{ active: liked }" @click="toggleLike">
          <el-icon><Star /></el-icon>
          <span>{{ likeCount }}</span>
        </button>
        <button type="button" @click="submitComment">
          <el-icon><ChatDotRound /></el-icon>
          <span>{{ currentPost.comments }}</span>
        </button>
        <button type="button" :class="{ active: isFavorited }" @click="toggleFavorite">
          <el-icon><Collection /></el-icon>
          <span>{{ saveCount }}</span>
        </button>
        <button type="button" @click="emit('action', `分享：${currentPost.title}`)">
          <el-icon><Share /></el-icon>
          <span>分享</span>
        </button>
      </div>
      <div class="short-video-switch">
        <button type="button" :disabled="currentVideoIndex <= 0" aria-label="上一个视频" @click="switchVideo(-1)">
          <el-icon><CaretTop /></el-icon>
        </button>
        <button type="button" :disabled="currentVideoIndex >= videos.length - 1" aria-label="下一个视频" @click="switchVideo(1)">
          <el-icon><CaretBottom /></el-icon>
        </button>
      </div>
    </section>

    <section class="video-comment-panel">
      <div class="section-head">
        <h2>评论区</h2>
        <span class="meta">{{ currentPost.comments }} 条</span>
      </div>
      <div class="comment-list">
        <div v-for="comment in comments" :key="comment.id" class="comment-item dark">
          <strong>{{ comment.author }}</strong>
          <p>{{ comment.text }}</p>
        </div>
      </div>
      <form class="comment-composer" @submit.prevent="submitComment">
        <input v-model="commentText" type="text" placeholder="说点什么..." />
        <button type="submit">发送</button>
      </form>
    </section>
  </section>

  <section v-else class="post-detail-page">
    <header class="post-detail-head">
      <el-button text class="back-link" :icon="ArrowLeft" @click="emit('back')">{{ backLabel }}</el-button>
    </header>

    <div class="post-image-rail">
      <div
        v-for="(image, index) in postImages(currentPost)"
        :key="image.id"
        :class="['post-image', `cover-${image.tone}`]"
      >
        <span>图文 {{ index + 1 }}</span>
      </div>
    </div>

    <article class="post-detail-body">
      <button type="button" class="community-detail-author community-detail-author-button" @click="emit('open-author', currentPost)">
        <el-avatar :size="40">{{ currentPost.avatar }}</el-avatar>
        <div class="community-detail-author-copy">
          <strong>{{ currentPost.author }}</strong>
          <p class="meta">{{ currentPost.publishedAt }} · {{ currentPost.postType }}</p>
        </div>
        <span class="author-profile-hint">查看主页</span>
      </button>

      <h1>{{ currentPost.title }}</h1>
      <p class="community-detail-text">{{ currentPost.excerpt }}</p>
      <div class="chips compact">
        <el-tag v-for="tag in currentPost.tags" :key="tag" round effect="light" size="small">{{ tag }}</el-tag>
      </div>

      <div class="community-detail-actions">
        <button type="button" :class="{ active: liked }" @click="toggleLike">
          <el-icon><Star /></el-icon>{{ likeCount }}
        </button>
        <button type="button" @click="submitComment">
          <el-icon><ChatDotRound /></el-icon>{{ currentPost.comments }}
        </button>
        <button type="button" :class="{ active: isFavorited }" @click="toggleFavorite">
          <el-icon><Collection /></el-icon>{{ saveCount }}
        </button>
        <button type="button" @click="emit('action', `分享：${currentPost.title}`)">
          <el-icon><Share /></el-icon>分享
        </button>
      </div>

      <section class="detail-section">
        <h4>评论区 · {{ currentPost.comments }}</h4>
        <div class="comment-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <strong>{{ comment.author }}</strong>
            <p>{{ comment.text }}</p>
          </div>
        </div>
        <form class="comment-composer" @submit.prevent="submitComment">
          <input v-model="commentText" type="text" placeholder="写评论" />
          <button type="submit">发送</button>
        </form>
      </section>
    </article>
  </section>
</template>
