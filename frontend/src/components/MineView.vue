<script setup>
import { computed, ref } from "vue";
import PostViewer from "./PostViewer.vue";
import { Close } from "@element-plus/icons-vue";
import { createReport, fetchProfileSummary, fetchServiceRecommendations } from "../services/api";

const props = defineProps({
  currentUserId: {
    type: String,
    default: "demo_user"
  },
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
  },
  user: {
    type: Object,
    default: null
  },
  membership: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(["action", "toggle-favorite", "navigate"]);

const activePane = ref("records");
const selectedRecord = ref(null);
const selectedPost = ref(null);
const showReport = ref(false);
const reportLoading = ref(false);
const reportData = ref(null);
const serviceRecommendations = ref(null);

const userNickname = computed(() => props.user?.nickname || "钓友");
const userCity = computed(() => props.user?.city || "未知城市");
const userPreferredMethods = computed(() => props.user?.preferred_methods?.join("、") || "暂无偏好");
const isMember = computed(() => props.membership?.status === "active");
const memberExpiry = computed(() => {
  if (!props.membership?.expires_at) return "";
  return new Date(props.membership.expires_at).toLocaleDateString("zh-CN");
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

const blankTripCount = computed(() => {
  return props.records.filter((r) => r.is_blank_trip || (Number(r.fish_count) === 0 && r.fish_species === null)).length;
});

const dataSufficient = computed(() => props.records.length >= 5);

const mostUsedMethod = computed(() => {
  const map = {};
  props.records.forEach((r) => {
    const m = r.fishing_method || "未填写";
    map[m] = (map[m] || 0) + 1;
  });
  const best = Object.entries(map).sort((a, b) => b[1] - a[1])[0];
  return best ? best[0] : "待记录";
});

const mostEfficientMethod = computed(() => {
  const efficiency = {};
  props.records.forEach((r) => {
    const m = r.fishing_method || "未填写";
    const hours = (Number(r.duration_seconds) || 0) / 3600;
    if (hours > 0) {
      const rate = (Number(r.fish_count) || 0) / hours;
      if (!efficiency[m]) efficiency[m] = [];
      efficiency[m].push(rate);
    }
  });
  const avg = {};
  for (const [m, rates] of Object.entries(efficiency)) {
    avg[m] = rates.reduce((a, b) => a + b, 0) / rates.length;
  }
  const best = Object.entries(avg).sort((a, b) => b[1] - a[1])[0];
  return best ? best[0] : "待记录";
});

const preferredTimeSlot = computed(() => {
  const morning = props.records.filter((r) => {
    const h = new Date(r.start_time || r.created_at).getHours();
    return h >= 5 && h < 10;
  }).length;
  const afternoon = props.records.filter((r) => {
    const h = new Date(r.start_time || r.created_at).getHours();
    return h >= 14 && h < 18;
  }).length;
  const evening = props.records.filter((r) => {
    const h = new Date(r.start_time || r.created_at).getHours();
    return h >= 18 && h < 22;
  }).length;
  if (morning >= afternoon && morning >= evening) return "清晨 05:00-09:00";
  if (afternoon >= evening) return "午后 14:00-17:00";
  return "傍晚 18:00-21:00";
});

const preferredTempRange = computed(() => {
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
  if (record.is_blank_trip) return "空军 · " + (record.blank_reason || "未填写原因");
  return `${species} · ${count}尾 · ${weight}斤`;
}

function openRecord(record) {
  selectedRecord.value = record;
}

function openPost(post) {
  selectedPost.value = post;
}

function handleReportClick() {
  if (!isMember.value) {
    emit("action", "请先升级为鱼你有图会员以解锁专属报告");
    showUpgradeModal.value = true;
    return;
  }
  generateReport();
}

async function generateReport() {
  reportLoading.value = true;
  showReport.value = true;
  try {
    const data = await fetchProfileSummary(props.currentUserId);
    reportData.value = data;
    serviceRecommendations.value = await fetchServiceRecommendations(props.currentUserId);
  } catch {
    reportData.value = null;
  }
  try {
    await createReport(props.currentUserId, "lifetime");
  } catch {
    // snapshot save is best-effort
  }
  reportLoading.value = false;
}

const showUpgradeModal = ref(false);

async function saveAndShareReport() {
  const canvas = document.createElement("canvas");
  const w = 750;
  const h = 1200;
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");

  const bg = ctx.createLinearGradient(0, 0, 0, h);
  bg.addColorStop(0, "#e8f4f0");
  bg.addColorStop(0.3, "#d4eae8");
  bg.addColorStop(0.7, "#f5f2eb");
  bg.addColorStop(1, "#faf8f2");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, w, h);

  ctx.fillStyle = "rgba(26,122,138,0.04)";
  ctx.beginPath(); ctx.arc(620, 100, 180, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.arc(100, 1050, 140, 0, Math.PI * 2); ctx.fill();

  ctx.fillStyle = "#0d4f5a";
  ctx.font = "bold 42px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("鱼你有图 · 会员专属报告", 50, 80);

  ctx.fillStyle = "#7a8a7e";
  ctx.font = "22px 'PingFang SC','Microsoft YaHei',sans-serif";
  const now = new Date();
  ctx.fillText(`生成日期：${now.getFullYear()}/${now.getMonth() + 1}/${now.getDate()}`, 50, 125);

  ctx.strokeStyle = "rgba(26,122,138,0.15)";
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(50, 155); ctx.lineTo(700, 155); ctx.stroke();

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

  ctx.fillStyle = "#0d4f5a";
  ctx.font = "bold 28px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("钓鱼偏好", 50, 310);

  const prefRows = [
    ["常用钓法", mostUsedMethod.value],
    ["偏好时段", preferredTimeSlot.value],
    ["常钓气温", preferredTempRange.value],
    ["常钓鱼种", topSpecies.value[0]?.[0] || "待记录"]
  ];
  let ry = 355;
  prefRows.forEach(([label, value]) => {
    ctx.fillStyle = "#7a8a7e";
    ctx.font = "22px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(label, 60, ry);
    ctx.fillStyle = "#1a7a8a";
    ctx.font = "bold 22px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(value, 240, ry);
    ry += 48;
  });

  ctx.fillStyle = "#0d4f5a";
  ctx.font = "bold 28px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("效率分析", 50, ry + 20);
  ry += 60;

  if (dataSufficient.value) {
    const effRows = [
      ["最高效钓法(尾/时)", mostEfficientMethod.value],
      ["空军率", `${blankTripCount.value}次 / ${props.records.length}次`]
    ];
    effRows.forEach(([label, value]) => {
      ctx.fillStyle = "#7a8a7e";
      ctx.font = "22px 'PingFang SC','Microsoft YaHei',sans-serif";
      ctx.fillText(label, 60, ry);
      ctx.fillStyle = "#1a7a8a";
      ctx.font = "bold 22px 'PingFang SC','Microsoft YaHei',sans-serif";
      ctx.fillText(value, 240, ry);
      ry += 48;
    });
  } else {
    ctx.fillStyle = "#7a8a7e";
    ctx.font = "22px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText("数据积累中（需至少5次出钓记录）", 60, ry);
    ry += 48;
  }

  ctx.fillStyle = "#0d4f5a";
  ctx.font = "bold 28px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText("高频钓点", 50, ry + 20);
  ry += 60;

  topSpots.value.forEach((s, i) => {
    const medal = ["🥇", "🥈", "🥉"][i] || "📍";
    ctx.font = "24px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(`${medal}  ${s[0]}`, 60, ry);
    ctx.fillStyle = "#1a7a8a";
    ctx.font = "bold 22px 'PingFang SC','Microsoft YaHei',sans-serif";
    ctx.fillText(`${s[1]}次`, 560, ry);
    ctx.fillStyle = "#0d4f5a";
    ry += 44;
  });

  const memberStatus = isMember.value ? "鱼你有图会员" : "非会员";
  ctx.fillStyle = "#7a8a7e";
  ctx.font = "18px 'PingFang SC','Microsoft YaHei',sans-serif";
  ctx.fillText(`鱼你有图 · ${memberStatus} · 专属定制`, 50, h - 60);
  ctx.fillText("VIP Fishing Report · FishMan", 50, h - 30);

  const blob = await new Promise((r) => canvas.toBlob(r, "image/png"));
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `鱼你有图_会员报告_${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, "0")}${String(now.getDate()).padStart(2, "0")}.png`;
  a.click();
  URL.revokeObjectURL(url);

  emit("action", "报告截图已保存");

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
        <el-tag v-if="selectedRecord.is_blank_trip" round type="warning" effect="light">空军</el-tag>
        <el-tag v-else round type="success" effect="light">记录</el-tag>
      </div>
      <div class="mine-record-stats">
        <div><span>鱼获</span><strong>{{ recordCatch(selectedRecord) }}</strong></div>
        <div><span>钓法</span><strong>{{ selectedRecord.fishing_method || "未填写" }}</strong></div>
        <div><span>饵料</span><strong>{{ selectedRecord.bait || "未填写" }}</strong></div>
        <div><span>位置</span><strong>{{ selectedRecord.location_name || "未记录" }}</strong></div>
        <div v-if="selectedRecord.max_single_weight"><span>最大单尾</span><strong>{{ selectedRecord.max_single_weight }}斤</strong></div>
      </div>
      <section v-if="selectedRecord.is_blank_trip && selectedRecord.blank_reason" class="detail-section">
        <h4>空军原因</h4>
        <p class="community-detail-text">{{ selectedRecord.blank_reason }}</p>
      </section>
      <section class="detail-section">
        <h4>本次复盘</h4>
        <p class="community-detail-text">{{ selectedRecord.note || "还没有补充复盘内容。" }}</p>
      </section>
    </article>
  </section>

  <section v-else class="card profile-panel">
    <div class="row">
      <div>
        <h2>{{ userNickname }}</h2>
        <p class="meta">偏好：{{ userPreferredMethods }}</p>
      </div>
      <el-tag v-if="isMember" round type="primary" effect="light">鱼你有图会员</el-tag>
      <el-tag v-else round type="info" effect="light">非会员</el-tag>
    </div>
    <div class="stat-grid">
      <div class="stat"><strong>{{ records.length }}</strong><span class="meta">出钓</span></div>
      <div class="stat"><strong>{{ heatmapSpots.length }}</strong><span class="meta">钓点</span></div>
      <div class="stat"><strong>{{ totalWeight }}斤</strong><span class="meta">总重量</span></div>
    </div>
  </section>

  <section v-if="!selectedPost && !selectedRecord" class="section poi-list">
    <article :class="['vip-card', isMember ? 'vip-active' : 'vip-inactive']">
      <div class="vip-card-glow"></div>
      <div class="vip-badge-row">
        <span class="vip-tier-badge">
          <span v-if="isMember">鱼你有图会员</span>
          <span v-else>升级会员解锁专属报告</span>
        </span>
        <span v-if="isMember && memberExpiry" class="vip-expire">有效期至 {{ memberExpiry }}</span>
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
      <div v-if="!isMember" class="vip-upgrade-cta">
        <strong>解锁会员专属报告</strong>
        <p>查看钓鱼偏好分析、效率统计、钓点排行和AI推荐</p>
        <div class="vip-upgrade-features">
          <span>偏好分析</span>
          <span>效率统计</span>
          <span>钓点排行</span>
          <span>报告分享</span>
        </div>
        <el-button class="vip-report-btn" type="warning" round @click="showUpgradeModal = true">
          立即升级会员 · ¥9.9/月
        </el-button>
        <p class="meta" style="text-align:center;margin-top:6px;font-size:11px;">非会员可完整记录和使用社区，报告能力受限</p>
      </div>
      <el-button v-else class="vip-report-btn" type="primary" round :loading="reportLoading" @click="generateReport">
        生成专属会员报告
      </el-button>
    </article>
  </section>

  <Transition name="modal">
    <div v-if="showReport" class="report-modal-overlay" @click.self="showReport = false">
      <div class="report-modal">
        <header class="report-hero">
          <button class="report-close-btn" type="button" aria-label="关闭会员报告" @click="showReport = false">
            <el-icon><Close /></el-icon>
          </button>
          <div class="report-sun"></div>
          <div class="report-mountain report-mountain-back"></div>
          <div class="report-mountain report-mountain-front"></div>
          <div class="report-water"></div>
          <div class="report-angler">
            <span class="report-angler-head"></span>
            <span class="report-angler-body"></span>
            <span class="report-rod"></span>
          </div>
          <div class="report-hero-content">
            <div class="report-brand">鱼你有图 <span>FISH ON</span></div>
            <h2>会员专属报告</h2>
            <div class="report-member-badge"><span>&#9830;</span> {{ isMember ? '鱼你有图会员' : '非会员' }}</div>
            <p class="report-date">生成日期：{{ new Date().toLocaleDateString("zh-CN") }}</p>
          </div>
        </header>

        <div class="report-modal-body">
          <section class="report-summary" aria-label="钓鱼数据总览">
            <div class="report-summary-item">
              <strong>{{ records.length }}</strong>
              <span class="report-summary-icon">&#9001;</span>
              <small>总出钓</small>
            </div>
            <div class="report-summary-item">
              <strong>{{ totalCatches }}</strong>
              <span class="report-summary-icon">鱼</span>
              <small>总鱼获(尾)</small>
            </div>
            <div class="report-summary-item">
              <strong>{{ totalWeight }}</strong>
              <span class="report-summary-icon">斤</span>
              <small>总重量(斤)</small>
            </div>
            <div class="report-summary-item">
              <strong>{{ heatmapSpots.length }}</strong>
              <span class="report-summary-icon">&#8998;</span>
              <small>探钓点</small>
            </div>
          </section>

          <article class="report-panel report-preference">
            <h3><span></span>钓鱼偏好（按出现频率）</h3>
            <div class="report-detail-list">
              <div class="report-detail-row">
                <span class="report-detail-icon">&#9703;</span>
                <span>偏好时段</span>
                <strong>{{ preferredTimeSlot }}</strong>
              </div>
              <div class="report-detail-row">
                <span class="report-detail-icon">&#9832;</span>
                <span>常钓气温</span>
                <strong>{{ preferredTempRange }}</strong>
              </div>
              <div class="report-detail-row">
                <span class="report-detail-icon">&#8971;</span>
                <span>常用钓法</span>
                <strong>{{ mostUsedMethod }}</strong>
              </div>
              <div class="report-detail-row">
                <span class="report-detail-icon">鱼</span>
                <span>常钓鱼种</span>
                <strong>{{ topSpecies[0]?.[0] || "待记录" }}</strong>
              </div>
            </div>
          </article>

          <article class="report-panel report-efficiency">
            <h3><span></span>效率分析（单位时间鱼获）</h3>
            <div v-if="dataSufficient" class="report-detail-list">
              <div class="report-detail-row">
                <span class="report-detail-icon">&#8971;</span>
                <span>最高效钓法</span>
                <strong>{{ mostEfficientMethod }}</strong>
              </div>
              <div class="report-detail-row">
                <span class="report-detail-icon">&#8854;</span>
                <span>空军率</span>
                <strong>{{ blankTripCount }}次 / {{ records.length }}次</strong>
              </div>
            </div>
            <div v-else class="report-empty">数据积累中 — 记录达到5次出钓后，这里会展示效率分析</div>
          </article>

          <article class="report-panel report-spots">
            <h3><span></span>高频钓点</h3>
            <div v-if="topSpots.length" class="report-spot-list">
              <div v-for="(spot, index) in topSpots" :key="spot[0]" class="report-spot-row">
                <span :class="['report-medal', `report-medal-${index + 1}`]">{{ index + 1 }}</span>
                <strong>{{ spot[0] }}</strong>
                <b>{{ spot[1] }}次</b>
              </div>
            </div>
            <div v-else class="report-empty">记录首次出钓后，这里会生成你的钓点排行</div>
          </article>

          <article class="report-panel report-recommend">
            <h3><span>&#987;</span>从报告到下一步行动</h3>
            <div class="report-recommend-list">
              <button type="button" @click="showReport = false; emit('navigate', 'tutorials')">
                <span>&#9733;</span>
                <p>推荐教程：<strong>{{ serviceRecommendations?.tutorial?.item?.title || "新手调漂与复盘" }}</strong><small>{{ serviceRecommendations?.tutorial?.reason }}</small></p>
              </button>
              <button type="button" @click="showReport = false; emit('navigate', 'services')">
                <span>&#9873;</span>
                <p>推荐活动：<strong>{{ serviceRecommendations?.event?.item?.title || "同城约钓活动" }}</strong><small>{{ serviceRecommendations?.event?.reason }}</small></p>
              </button>
              <button type="button" @click="showReport = false; emit('navigate', 'services')">
                <span>&#9874;</span>
                <p>推荐装备：<strong>{{ serviceRecommendations?.equipment?.item?.name || "真实战绩装备" }}</strong><small>{{ serviceRecommendations?.equipment?.reason }}</small></p>
              </button>
            </div>
          </article>

          <footer class="report-footer">
            <p><span></span> 鱼你有图 · {{ isMember ? '会员' : '非会员' }} · 专属定制 <span></span></p>
            <small>VIP Fishing Report · FishMan</small>
          </footer>

          <button class="vip-share-btn" type="button" @click="saveAndShareReport">
            <span>&#8675;</span> 保存报告并分享
          </button>
        </div>
      </div>
    </div>
  </Transition>

  <!-- Upgrade modal for non-members -->
  <Transition name="modal">
    <div v-if="showUpgradeModal" class="report-modal-overlay" @click.self="showUpgradeModal = false">
      <div class="report-modal" style="max-width:360px;">
        <header class="report-hero" style="min-height:180px;">
          <button class="report-close-btn" type="button" @click="showUpgradeModal = false">
            <el-icon><Close /></el-icon>
          </button>
          <div class="report-hero-content">
            <div class="report-brand" style="font-size:18px;">鱼你有图 <span>FISH ON</span></div>
            <h2 style="font-size:20px;">升级会员</h2>
            <p class="report-date">解锁完整钓鱼数据分析</p>
          </div>
        </header>
        <div class="report-modal-body" style="padding:20px;">
          <div style="text-align:center;margin-bottom:16px;">
            <strong style="font-size:28px;color:var(--blue);">¥9.9</strong>
            <span class="meta"> / 月</span>
          </div>
          <div style="display:grid;gap:8px;margin-bottom:18px;">
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;">
              <span style="color:#34c759;font-weight:700;">&#10003;</span> 钓鱼偏好分析（时段/气温/钓法/鱼种）
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;">
              <span style="color:#34c759;font-weight:700;">&#10003;</span> 效率分析（单位时间鱼获率/空军率）
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;">
              <span style="color:#34c759;font-weight:700;">&#10003;</span> 高频钓点排行与路线推荐
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;">
              <span style="color:#34c759;font-weight:700;">&#10003;</span> 会员报告生成与分享
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:6px 0;">
              <span style="color:#34c759;font-weight:700;">&#10003;</span> 月报/年报/生涯报告历史
            </div>
          </div>
          <el-button type="primary" round style="width:100%;" @click="showUpgradeModal = false; emit('action', '演示模式：会员升级仅展示UI流程')">
            立即升级（演示）
          </el-button>
          <p class="meta" style="text-align:center;margin-top:10px;font-size:11px;">当前为演示模式，会员升级仅展示UI流程</p>
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
          <el-tag v-else-if="record.is_blank_trip" round type="warning" effect="light">空军</el-tag>
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
            <el-tag round type="info" effect="plain">{{ post.visibility === 'public' ? '公开' : post.visibility === 'friends' ? '朋友' : '私密' }}</el-tag>
            <el-tag v-if="post.fish_species?.length" round type="primary" effect="light">{{ post.fish_species.join('、') }}</el-tag>
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
