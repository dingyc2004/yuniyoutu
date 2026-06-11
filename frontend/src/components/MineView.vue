<script setup>
import { computed, ref } from "vue";
import PostViewer from "./PostViewer.vue";

const props = defineProps({
  records: {
    type: Array,
    default: () => []
  },
  posts: {
    type: Array,
    default: () => []
  },
  favorites: {
    type: Array,
    default: () => []
  },
  feed: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(["action", "toggle-favorite"]);

const activePane = ref("records");
const selectedRecord = ref(null);
const selectedPost = ref(null);

const maxFishWeight = computed(() => {
  const max = props.records.reduce((best, record) => Math.max(best, Number(record.fish_weight) || 0), 0);
  return max ? `${max}斤` : "0斤";
});

function formatDateTime(value) {
  if (!value) return "时间未记录";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "时间未记录";
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false
  }).format(date);
}

function formatDuration(seconds) {
  const total = Number(seconds) || 0;
  if (!total) return "未计时";
  const hours = Math.floor(total / 3600);
  const minutes = Math.floor((total % 3600) / 60);
  if (hours) return `${hours}小时${minutes}分钟`;
  return `${Math.max(minutes, 1)}分钟`;
}

function recordTitle(record) {
  return record.fishing_spot_name || record.location_name || "未命名钓鱼记录";
}

function recordMeta(record) {
  return [
    formatDateTime(record.start_time || record.created_at),
    formatDuration(record.duration_seconds),
    record.weather,
    record.temperature != null ? `${record.temperature}℃` : ""
  ]
    .filter(Boolean)
    .join(" · ");
}

function recordCatch(record) {
  const species = record.fish_species || "未填写鱼种";
  const count = Number(record.fish_count) || 0;
  const weight = Number(record.fish_weight) || 0;
  return `${species} · ${count}尾 · ${weight}斤`;
}

function openRecord(record) {
  selectedRecord.value = record;
}

function openPost(post) {
  selectedPost.value = post;
}
</script>

<template>
  <PostViewer
    v-if="selectedPost"
    :post="selectedPost"
    :feed="[...posts, ...feed]"
    :favorites="favorites"
    back-label="返回我的"
    @back="selectedPost = null"
    @action="(message) => emit('action', message)"
    @toggle-favorite="(post) => emit('toggle-favorite', post)"
  />

  <section v-else-if="selectedRecord" class="mine-record-detail">
    <el-button text class="back-link" @click="selectedRecord = null">返回我的记录</el-button>
    <article class="card mine-record-detail-card">
      <div class="mine-record-head">
        <div>
          <h2>{{ recordTitle(selectedRecord) }}</h2>
          <p class="meta">{{ recordMeta(selectedRecord) }}</p>
        </div>
        <el-tag round type="success" effect="light">记录</el-tag>
      </div>
      <div class="mine-record-stats">
        <div><span>鱼获</span><strong>{{ recordCatch(selectedRecord) }}</strong></div>
        <div><span>钓法</span><strong>{{ selectedRecord.fishing_method || "未填写" }}</strong></div>
        <div><span>饵料</span><strong>{{ selectedRecord.bait || "未填写" }}</strong></div>
        <div><span>位置</span><strong>{{ selectedRecord.location_name || "未记录" }}</strong></div>
      </div>
      <section class="detail-section">
        <h4>本次复盘</h4>
        <p class="community-detail-text">{{ selectedRecord.note || "还没有补充复盘内容。" }}</p>
      </section>
    </article>
  </section>

  <section v-else class="card profile-panel">
    <div class="row">
      <div>
        <h2>武汉钓友 008</h2>
        <p class="meta">偏好：野钓、路亚、清晨窗口</p>
      </div>
      <el-tag round type="primary" effect="light">探点官</el-tag>
    </div>
    <div class="stat-grid">
      <div class="stat"><strong>{{ records.length }}</strong><span class="meta">出钓</span></div>
      <div class="stat"><strong>6</strong><span class="meta">钓点</span></div>
      <div class="stat"><strong>{{ maxFishWeight }}</strong><span class="meta">总重量</span></div>
    </div>
  </section>

  <section v-if="!selectedPost && !selectedRecord" class="section poi-list">
    <article class="card poi-card">
      <h3>本月报告</h3>
      <p class="meta">你在气温 20-26℃、风力 1-3 级时鱼获率最高。东湖听涛和青山江滩是你的高频点。</p>
      <el-button type="primary" round>生成会员报告</el-button>
    </article>
  </section>

  <section v-if="!selectedPost && !selectedRecord" class="section">
    <div class="mine-tabs" aria-label="我的内容">
      <button type="button" :class="{ active: activePane === 'records' }" @click="activePane = 'records'">
        我的记录 <span>{{ records.length }}</span>
      </button>
      <button type="button" :class="{ active: activePane === 'posts' }" @click="activePane = 'posts'">
        我的发布 <span>{{ posts.length }}</span>
      </button>
      <button type="button" :class="{ active: activePane === 'favorites' }" @click="activePane = 'favorites'">
        收藏夹 <span>{{ favorites.length }}</span>
      </button>
    </div>

    <div v-if="activePane === 'records'" class="mine-post-list">
      <article v-if="!records.length" class="card poi-card">
        <h3>还没有钓鱼记录</h3>
        <p class="meta">在记录页完成一次钓鱼记录后，会同步显示在这里。</p>
      </article>

      <article
        v-for="record in records"
        :key="record.id || record.start_time"
        class="mine-record-card clickable"
        role="button"
        tabindex="0"
        @click="openRecord(record)"
        @keydown.enter.prevent="openRecord(record)"
      >
        <div class="mine-record-head">
          <div>
            <h3>{{ recordTitle(record) }}</h3>
            <p class="meta">{{ recordMeta(record) }}</p>
          </div>
          <el-tag v-if="record.offline" round type="warning" effect="light">本机</el-tag>
          <el-tag v-else round type="success" effect="light">已保存</el-tag>
        </div>
        <div class="mine-record-stats">
          <div><span>鱼获</span><strong>{{ recordCatch(record) }}</strong></div>
          <div><span>钓法</span><strong>{{ record.fishing_method || "未填写" }}</strong></div>
        </div>
        <p v-if="record.note" class="meta mine-record-note">{{ record.note }}</p>
      </article>
    </div>

    <div v-else-if="activePane === 'posts'" class="mine-post-list">
      <article v-if="!posts.length" class="card poi-card">
        <h3>还没有发布内容</h3>
        <p class="meta">发布图文或视频后，会在这里看到自己的鱼获记录。</p>
      </article>

      <article
        v-for="post in posts"
        :key="post.id"
        class="mine-post-card"
        role="button"
        tabindex="0"
        @click="openPost(post)"
        @keydown.enter.prevent="openPost(post)"
      >
        <div :class="['mine-post-cover', `tone-${post.coverTone || 'blue'}`]">
          <span>{{ post.format }}</span>
        </div>
        <div>
          <h3>{{ post.title }}</h3>
          <p class="meta">{{ post.meta }}</p>
          <div class="chips compact">
            <el-tag round type="info" effect="plain">{{ post.privacy }}</el-tag>
            <el-tag v-if="post.catch" round type="primary" effect="light">{{ post.catch.species }} / {{ post.catch.weight }}</el-tag>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="mine-post-list">
      <article v-if="!favorites.length" class="card poi-card">
        <h3>收藏夹还是空的</h3>
        <p class="meta">在帖子或短视频详情里点收藏后，会同步到这里。</p>
      </article>

      <article
        v-for="post in favorites"
        :key="post.id"
        class="mine-post-card"
        role="button"
        tabindex="0"
        @click="openPost(post)"
        @keydown.enter.prevent="openPost(post)"
      >
        <div :class="['mine-post-cover', `tone-${post.coverTone || 'blue'}`]">
          <span>{{ post.format }}</span>
        </div>
        <div>
          <h3>{{ post.title }}</h3>
          <p class="meta">{{ post.meta }}</p>
          <div class="chips compact">
            <el-tag round type="info" effect="plain">{{ post.author || "钓友" }}</el-tag>
            <el-tag round type="primary" effect="light">{{ post.postType || post.post_type || "收藏" }}</el-tag>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>
