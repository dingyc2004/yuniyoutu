<script setup>
import { computed, ref } from "vue";
import PostViewer from "./PostViewer.vue";
import { Close } from "@element-plus/icons-vue";

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
const showReport = ref(false);
const memberTier = ref("gold");

const maxFishWeight = computed(() => {
  const max = props.records.reduce((best, record) => Math.max(best, Number(record.fish_weight) || 0), 0);
  return max ? `${max}斤` : "0斤";
});

const totalCatches = computed(() => {
  return props.records.reduce((sum, r) => sum + (Number(r.fish_count) || 0), 0);
});

const totalWeight = computed(() => {
  return props.records.reduce((sum, r) => sum + (Number(r.fish_weight) || 0), 0).toFixed(1);
});

const topSpecies = computed(() => {
  const map = {};
  props.records.forEach((r) => {
    const s = r.fish_species || "未知";
    map[s] = (map[s] || 0) + (Number(r.fish_count) || 0);
  });
  return Object.entries(map).sort((a, b) => b[1] - a[1]).slice(0, 3);
});

const topSpots = computed(() => {
  const map = {};
  props.records.forEach((r) => {
    const spot = r.fishing_spot_name || r.location_name || "未知钓点";
    map[spot] = (map[spot] || 0) + 1;
  });
  return Object.entries(map).sort((a, b) => b[1] - a[1]).slice(0, 3);
});

const bestTimeWindow = computed(() => {
  const morning = props.records.filter((r) => {
    const h = new Date(r.start_time || r.created_at).getHours();
    return h >= 5 && h < 10;
  }).length;
  const afternoon = props.records.filter((r) => {
    const h = new Date(r.start_time || r.created_at).getHours();
    return h >= 14 && h < 18;
  }).length;
  if (morning >= afternoon) return "清晨 05:00-09:00";
  return "午后 14:00-17:00";
});

const bestTempRange = computed(() => {
  const counts = {};
  props.records.forEach((r) => {
    if (r.temperature != null) {
      const t = Math.round(Number(r.temperature) / 5) * 5;
      const key = `${t}-${t + 5}℃`;
      counts[key] = (counts[key] || 0) + 1;
    }
  });
  const best = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
  return best ? best[0] : "20-25℃";
});

const bestMethod = computed(() => {
  const map = {};
  props.records.forEach((r) => {
    const m = r.fishing_method || "台钓";
    map[m] = (map[m] || 0) + 1;
  });
  const best = Object.entries(map).sort((a, b) => b[1] - a[1])[0];
  return best ? best[0] : "台钓";
});

const heatmapSpots = computed(() => {
  return props.records.reduce((acc, r) => {
    const spot = r.fishing_spot_name || r.location_name || "未知";
    const existing = acc.find((s) => s.name === spot);
    if (existing) {
      existing.count++;
      existing.weight += Number(r.fish_weight) || 0;
    } else {
      acc.push({ name: spot, count: 1, weight: Number(r.fish_weight) || 0 });
    }
    return acc;
  }, []);
});

const maxHeatCount = computed(() => {
  return Math.max(1, ...heatmapSpots.value.map((s) => s.count));
});

const memberBenefits = computed(() => [
  { icon: "🎯", title: "专属钓鱼热力图", desc: "基于你的记录生成个人钓点热度分析" },
  { icon: "🤖", title: "智能每日推荐", desc: "AI 分析天气+鱼情，推送最适合你的钓点" },
  { icon: "📊", title: "鱼获趋势分析", desc: "月度/季度鱼获统计与趋势预测" },
  { icon: "🔮", title: "季节性鱼种预测", desc: "根据历史数据预测近期高活性鱼种" },
  { icon: "🎓", title: "VIP 钓技课程", desc: "专业钓手的实战技巧视频，每月更新" },
  { icon: "🎫", title: "优先钓点预约", desc: "合作钓场黄金时段优先锁定" },
  { icon: "🎒", title: "智能装备推荐", desc: "根据你的钓法偏好推荐适配装备" },
  { icon: "👑", title: "尊贵身份标识", desc: "社区内金色会员徽章 + 专属头像框" },
  { icon: "📤", title: "数据自由导出", desc: "一键导出全部钓鱼数据为 CSV/PDF" },
  { icon: "🏆", title: "区域排行榜", desc: "查看本地钓友鱼获排名，争夺月度冠军" }
]);

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

async function saveAndShareReport() {
  const canvas = document.createElement("canvas");
  const w = 750;
  const h = 1200;
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");

  // background — water gradient
  const bg = ctx.createLinearGradient(0, 0, 0, h);
  bg.addColorStop(0, "#e8f4f0");
  bg.addColorStop(0.3, "#d4eae8");
  bg.addColorStop(0.7, "#f5f2eb");
  bg.addColorStop(1, "#faf8f2");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, w, h);

  // decorative circles
  ctx.fillStyle = "rgba(26,122,138,0.04)";
  ctx.beginPath(); ctx.arc(620, 100, 180, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(100, 1050, 140, 0, Math.PI * 2); ctx.fill();

  // title
  ctx.fillStyle = "#0d4f5a";
  ctx.font = "bold 42px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("鱼你有图 · 会员专属报告", 50, 80);

  // date
  ctx.fillStyle = "#7a8a7e";
  ctx.font = "22px 'PingFang SC','Microsoft YaHei',sans-serif";
  const now = new Date();
  ctx.fillText(`生成日期：${now.getFullYear()}/${now.getMonth()+1}/${now.getDate()}`, 50, 125);

  // divider
  ctx.strokeStyle = "rgba(26,122,138,0.15)";
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(50, 155); ctx.lineTo(700, 155); ctx.stroke();

  // stats row
  const stats = [
    { label: "总出钓", value: props.records.length },
    { label: "总鱼获(尾)", value: totalCatches.value },
    { label: "总重量(斤)", value: totalWeight.value },
    { label: "探钓点", value: heatmapSpots.value.length }
  ];
  let sx = 50;
  stats.forEach((s) => {
    ctx.fillStyle = "#0d4f5a";
    ctx.font = "bold 36px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(String(s.value), sx, 210);
    ctx.fillStyle = "#7a8a7e";
    ctx.font = "20px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(s.label, sx, 240);
    sx += 170;
  });

  // section: best analysis
  ctx.fillStyle = "#0d4f5a";
  ctx.font = "bold 28px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("偏好分析", 50, 310);

  const rows = [
    ["最佳时段", bestTimeWindow.value],
    ["最佳气温", bestTempRange.value],
    ["最高效钓法", bestMethod.value],
    ["常钓鱼种", topSpecies.value[0]?.[0] || "待记录"]
  ];
  let ry = 355;
  rows.forEach(([label, value]) => {
    ctx.fillStyle = "#7a8a7e";
    ctx.font = "22px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(label, 60, ry);
    ctx.fillStyle = "#1a7a8a";
    ctx.font = "bold 22px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(value, 240, ry);
    ry += 48;
  });

  // section: top spots
  ctx.fillStyle = "#0d4f5a";
  ctx.font = "bold 28px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("高频钓点", 50, ry + 20);
  ry += 60;

  topSpots.value.forEach((s, i) => {
    const medal = ["🥇","🥈","🥉"][i] || "📍";
    ctx.font = "24px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(`${medal}  ${s[0]}`, 60, ry);
    ctx.fillStyle = "#1a7a8a";
    ctx.font = "bold 22px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(`${s[1]}次`, 560, ry);
    ctx.fillStyle = "#0d4f5a";
    ry += 44;
  });

  // section: AI recommend
  ctx.fillStyle = "#0d4f5a";
  ctx.font = "bold 28px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("今日智能推荐", 50, ry + 20);
  ry += 60;

  const recs = [
    "🎯 推荐钓点：东湖听涛景区",
    "🕐 最佳窗口：明早 06:00-08:30",
    "🎣 推荐钓法：台钓 + 酒米打窝"
  ];
  recs.forEach((r) => {
    ctx.fillStyle = "#1e2520";
    ctx.font = "22px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(r, 60, ry);
    ry += 42;
  });

  // footer
  ctx.fillStyle = "#7a8a7e";
  ctx.font = "18px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("鱼你有图 · 金竿会员 · 专属定制", 50, h - 60);
  ctx.fillText("VIP Fishing Report · FishMan", 50, h - 30);

  // download
  const blob = await new Promise((r) => canvas.toBlob(r, "image/png"));
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `鱼你有图_会员报告_${now.getFullYear()}${String(now.getMonth()+1).padStart(2,"0")}${String(now.getDate()).padStart(2,"0")}.png`;
  a.click();
  URL.revokeObjectURL(url);

  emit("action", "报告截图已保存");

  // share
  if (navigator.share) {
    try {
      const file = new File([blob], a.download, { type: "image/png" });
      await navigator.share({ title: "鱼你有图 · 会员专属报告", files: [file] });
    } catch {
      // user cancelled
    }
  } else {
    emit("action", "长按图片即可分享给好友");
  }
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
      <div class="stat"><strong>{{ heatmapSpots.length }}</strong><span class="meta">钓点</span></div>
      <div class="stat"><strong>{{ totalWeight }}斤</strong><span class="meta">总重量</span></div>
    </div>
  </section>

  <section v-if="!selectedPost && !selectedRecord" class="section poi-list">
    <!-- VIP 会员卡 -->
    <article :class="['vip-card', `vip-${memberTier}`]">
      <div class="vip-card-glow"></div>
      <div class="vip-badge-row">
        <span class="vip-tier-badge">
          <span v-if="memberTier === 'gold'">👑 金竿会员</span>
          <span v-else-if="memberTier === 'silver'">🥈 银竿会员</span>
          <span v-else>🎣 普通会员</span>
        </span>
        <span class="vip-expire">有效期至 2027-06-12</span>
      </div>
      <div class="vip-stats-mini">
        <div class="vip-stat-mini">
          <span class="vip-stat-num">{{ records.length }}</span>
          <span class="vip-stat-label">总出钓</span>
        </div>
        <div class="vip-stat-mini">
          <span class="vip-stat-num">{{ totalCatches }}</span>
          <span class="vip-stat-label">总鱼获(尾)</span>
        </div>
        <div class="vip-stat-mini">
          <span class="vip-stat-num">{{ totalWeight }}</span>
          <span class="vip-stat-label">总重量(斤)</span>
        </div>
        <div class="vip-stat-mini">
          <span class="vip-stat-num">{{ heatmapSpots.length }}</span>
          <span class="vip-stat-label">探钓点</span>
        </div>
      </div>
      <el-button class="vip-report-btn" type="primary" round @click="showReport = true">
        📋 生成专属会员报告
      </el-button>
    </article>
  </section>

  <!-- 会员报告弹窗 -->
  <Transition name="modal">
    <div v-if="showReport" class="report-modal-overlay" @click.self="showReport = false">
      <div class="report-modal">
        <header class="report-modal-head">
          <h2>📋 专属会员报告</h2>
          <button class="drawer-close-btn" type="button" aria-label="关闭" @click="showReport = false">
            <el-icon><Close /></el-icon>
          </button>
        </header>
        <div class="report-modal-body">
          <!-- 热力图 -->
          <article class="card report-block">
            <h3>🔥 我的钓点热力榜</h3>
            <p class="meta">根据 {{ records.length }} 次出钓记录生成</p>
            <div class="heatmap-list">
              <div
                v-for="spot in heatmapSpots"
                :key="spot.name"
                class="heatmap-bar-row"
              >
                <span class="heatmap-label">{{ spot.name }}</span>
                <div class="heatmap-bar-track">
                  <div
                    class="heatmap-bar-fill"
                    :style="{ width: `${(spot.count / maxHeatCount) * 100}%` }"
                  ></div>
                </div>
                <span class="heatmap-val">{{ spot.count }}次 · {{ spot.weight.toFixed(1) }}斤</span>
              </div>
              <div v-if="!heatmapSpots.length" class="heatmap-empty">
                <p class="meta">完成钓鱼记录后，这里会展示你的钓点热力分布。</p>
              </div>
            </div>
          </article>

          <!-- 鱼获分析 -->
          <article class="card report-block">
            <h3>📊 鱼获偏好分析</h3>
            <div class="report-grid-2">
              <div class="report-stat-cell">
                <span class="report-stat-label">最佳时段</span>
                <strong class="report-stat-value">{{ bestTimeWindow }}</strong>
              </div>
              <div class="report-stat-cell">
                <span class="report-stat-label">最佳气温</span>
                <strong class="report-stat-value">{{ bestTempRange }}</strong>
              </div>
              <div class="report-stat-cell">
                <span class="report-stat-label">最高效钓法</span>
                <strong class="report-stat-value">{{ bestMethod }}</strong>
              </div>
              <div class="report-stat-cell">
                <span class="report-stat-label">常钓鱼种</span>
                <strong class="report-stat-value">{{ topSpecies[0]?.[0] || "待记录" }}</strong>
              </div>
            </div>
            <div v-if="topSpecies.length" class="species-rank">
              <h4>鱼种排行</h4>
              <div v-for="(s, i) in topSpecies" :key="s[0]" class="species-row">
                <span class="species-medal">{{ ['🥇','🥈','🥉'][i] }}</span>
                <span class="species-name">{{ s[0] }}</span>
                <span class="species-count">{{ s[1] }}尾</span>
              </div>
            </div>
            <div v-if="topSpots.length" class="species-rank">
              <h4>高频钓点</h4>
              <div v-for="(s, i) in topSpots" :key="s[0]" class="species-row">
                <span class="species-medal">{{ ['🥇','🥈','🥉'][i] || '📍' }}</span>
                <span class="species-name">{{ s[0] }}</span>
                <span class="species-count">{{ s[1] }}次</span>
              </div>
            </div>
          </article>

          <!-- 智能推荐 -->
          <article class="card report-block report-recommend">
            <h3>🤖 今日智能推荐</h3>
            <p class="meta">AI 综合天气、历史偏好、鱼情数据为你推荐</p>
            <div class="recommend-row">
              <div class="recommend-icon">🎯</div>
              <div class="recommend-body">
                <strong>推荐钓点：东湖听涛景区</strong>
                <p>你的历史高频点，今日适钓指数 78，东北风 2 级，鲫鱼活性高</p>
              </div>
            </div>
            <div class="recommend-row">
              <div class="recommend-icon">🕐</div>
              <div class="recommend-body">
                <strong>最佳窗口：明早 06:00-08:30</strong>
                <p>气温 22℃、气压稳定在 1016hPa，符合你的历史最佳出钓条件</p>
              </div>
            </div>
            <div class="recommend-row">
              <div class="recommend-icon">🎣</div>
              <div class="recommend-body">
                <strong>推荐钓法：台钓 + 酒米打窝</strong>
                <p>基于你 {{ bestMethod }} 的高成功率，搭配应季饵料配方</p>
              </div>
            </div>
          </article>

          <!-- VIP 权益列表 -->
          <article class="card report-block">
            <h3>👑 金竿会员全部权益</h3>
            <div class="benefits-grid">
              <div v-for="b in memberBenefits" :key="b.title" class="benefit-item">
                <span class="benefit-icon">{{ b.icon }}</span>
                <div>
                  <strong>{{ b.title }}</strong>
                  <p class="meta">{{ b.desc }}</p>
                </div>
              </div>
            </div>
          </article>

          <el-button class="vip-share-btn" type="primary" round size="large" @click="saveAndShareReport">
            📸 保存截图并分享报告
          </el-button>
        </div>
      </div>
    </div>
  </Transition>

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
