<script setup>
import { computed, onMounted, ref, watch } from "vue";
import {
  Bell,
  CirclePlus,
  Close,
  Search,
  Star
} from "@element-plus/icons-vue";
import ChatView from "./ChatView.vue";
import PostViewer from "./PostViewer.vue";
import PublishView from "./PublishView.vue";
import UserProfileView from "./UserProfileView.vue";
import { fetchCollection } from "../services/api";

const props = defineProps({
  currentUserId: { type: String, default: "demo_user" },
  openMessagesToken: { type: Number, default: 0 },
  shareRecord: { type: Object, default: null },
  feed: { type: Array, default: () => [] },
  favorites: { type: Array, default: () => [] },
  pois: { type: Array, default: () => [] },
  records: { type: Array, default: () => [] }
});

const emit = defineEmits(["action", "toggle-favorite", "submit-post", "share-consumed"]);

const showPublish = ref(false);
const showChat = ref(false);

const query = ref("");
const activeChannel = ref("推荐");
const selectedPost = ref(null);
const selectedUser = ref(null);

const groups = ref([]);
const messages = ref([]);
const messageCount = ref(10);
const contacts = ref([]);

const fallbackProfiles = {
  "江风路亚": { id: "user_jiangfeng", nickname: "江风路亚", avatar: "江", city: "武汉市", level: 4, bio: "江边搜索型路亚玩家，周末常驻青山江滩。", preferred_methods: ["路亚", "野钓"], preferred_species: ["翘嘴", "鳜鱼"] },
  "不空军的阿明": { id: "user_aming", nickname: "不空军的阿明", avatar: "明", city: "武汉市", level: 5, bio: "爱复盘饵料和窗口期，愿意带新手。", preferred_methods: ["台钓", "野钓"], preferred_species: ["鲫鱼", "鲤鱼"] },
  "钓场探路官": { id: "user_tanchang", nickname: "钓场探路官", avatar: "探", city: "武汉市", level: 3, bio: "记录武汉周边钓场体验和收费信息。", preferred_methods: ["台钓"], preferred_species: ["草鱼", "鲢鳙"] }
};

onMounted(async () => {
  const [gData, mData, socialData] = await Promise.all([
    fetchCollection("/api/groups", null).catch(() => []),
    fetchCollection("/api/groups/group_001/messages", null).catch(() => []),
    fetchCollection(`/api/users/${encodeURIComponent(props.currentUserId)}/social`, null).catch(() => [])
  ]);
  groups.value = Array.isArray(gData) ? gData : [];
  messages.value = Array.isArray(mData) ? mData : [];
  messageCount.value = Array.isArray(mData) ? mData.length : 0;
  contacts.value = Array.isArray(socialData) ? socialData : [];
  if (props.openMessagesToken > 0) showChat.value = true;
  if (props.shareRecord) showPublish.value = true;
});

watch(() => props.openMessagesToken, () => { showChat.value = true; });
watch(() => props.shareRecord, (record) => {
  if (record) showPublish.value = true;
}, { immediate: true });

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

function openAuthor(post) {
  const matched = contacts.value.find((user) => user.id === post.user_id || user.nickname === post.author);
  selectedUser.value = matched || fallbackProfiles[post.author] || {
    id: `user_${String(post.author || "angler").replace(/\s/g, "_")}`,
    nickname: post.author || "钓友",
    avatar: post.avatar || "钓",
    city: "武汉市",
    level: 2 + ((post.author || "").length % 4),
    bio: "喜欢记录鱼情、钓点和每一次出钓。",
    preferred_methods: [post.postType || "野钓"],
    preferred_species: post.fish_species || []
  };
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

function coverAspect(post) {
  const seed = (post.id || "").length + (post.imageCount || 1);
  const ratios = ["tall", "medium", "short"];
  return ratios[seed % ratios.length];
}
</script>

<template>
  <ChatView
    v-if="showChat"
    :groups="groups"
    :messages="messages"
    :contacts="contacts"
    :current-user-id="props.currentUserId"
    @action="(msg) => emit('action', msg)"
    @back="showChat = false"
  />

  <PostViewer
    v-else-if="selectedPost"
    :post="selectedPost"
    :feed="feedItems"
    :favorites="favorites"
    back-label="返回社区"
    @back="selectedPost = null"
    @action="(message) => emit('action', message)"
    @toggle-favorite="(post) => emit('toggle-favorite', post)"
    @open-author="openAuthor"
  />

  <UserProfileView
    v-else-if="selectedUser"
    :profile="selectedUser"
    :posts="feedItems"
    :current-user-id="props.currentUserId"
    @back="selectedUser = null"
    @action="(message) => emit('action', message)"
    @open-post="(post) => { selectedUser = null; selectedPost = post; }"
  />

  <section v-else class="community-page">
    <header class="community-topbar">
      <form class="community-search" @submit.prevent="submitSearch">
        <el-icon aria-hidden="true"><Search /></el-icon>
        <input v-model="query" type="search" placeholder="搜索钓点、鱼种、技巧、用户" />
      </form>
      <button type="button" class="community-publish-btn" aria-label="发布" @click="showPublish = true">
        <el-icon><CirclePlus /></el-icon>
        <span>发布</span>
      </button>
      <button type="button" class="community-msg-btn" aria-label="消息" @click="showChat = true">
        <el-icon><Bell /></el-icon>
        <span v-if="messageCount" class="msg-badge">{{ messageCount > 99 ? '99+' : messageCount }}</span>
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
              <button type="button" class="community-card-author" @click.stop="openAuthor(post)">
                <el-avatar :size="22">{{ post.avatar }}</el-avatar>
                <span>{{ post.author }}</span>
              </button>
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
              <button type="button" class="community-card-author" @click.stop="openAuthor(post)">
                <el-avatar :size="22">{{ post.avatar }}</el-avatar>
                <span>{{ post.author }}</span>
              </button>
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

    <Transition name="slide-up">
      <div v-if="showPublish" class="publish-overlay">
        <div class="publish-sheet">
          <header class="publish-sheet-head">
            <h2>发布动态</h2>
            <button class="drawer-close-btn" type="button" aria-label="关闭" @click="showPublish = false">
              <el-icon><Close /></el-icon>
            </button>
          </header>
          <div class="publish-sheet-body">
            <PublishView
              :current-user-id="props.currentUserId"
              :pois="pois"
              :records="records"
              :initial-record="props.shareRecord"
              @action="(msg) => emit('action', msg)"
              @submit-post="(post) => { emit('submit-post', post); emit('share-consumed'); showPublish = false; }"
            />
          </div>
        </div>
      </div>
    </Transition>
  </section>
</template>
