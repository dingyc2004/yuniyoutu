<script setup>
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { ArrowRight, Close, Delete, Picture, Plus } from "@element-plus/icons-vue";
import RecordLocationDialog from "./RecordLocationDialog.vue";
import { createFishingRecord } from "../services/api";

const props = defineProps({
  weatherText: { type: String, default: "天气待更新" },
  weather: { type: Object, default: () => ({}) }
});

const emit = defineEmits(["action", "record-saved"]);

const status = ref("idle");
const timer = ref(null);
const startAt = ref(null);
const endAt = ref(null);
const elapsedSeconds = ref(0);
const saving = ref(false);
const savedRecord = ref(null);
const locationPickerOpen = ref(false);
const contentBlocks = ref([]);
let nextContentBlockId = 1;

const session = reactive({
  fishingSpotName: "",
  locationName: "等待定位",
  latitude: null,
  longitude: null,
  note: ""
});

const summaryForm = reactive({
  fishing_spot_name: "",
  location_name: "",
  latitude: null,
  longitude: null,
  weather: "",
  temperature: null,
  fish_count: 0,
  fish_weight: 0,
  fish_species: "",
  fishing_method: "",
  bait: "",
  note: "",
  images: []
});

const liveWeather = computed(() => props.weather?.live || props.weather || {});
const weatherName = computed(() => liveWeather.value.weather || props.weatherText.split("·")[0]?.trim() || "多云");
const temperatureValue = computed(() => {
  const value = liveWeather.value.temperature ?? liveWeather.value.temperature_c ?? liveWeather.value.feels_like_c;
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
});

const timerLabel = computed(() => formatDuration(elapsedSeconds.value));
const startTimeLabel = computed(() => (startAt.value ? formatDateTime(startAt.value) : "尚未开始"));
const endTimeLabel = computed(() => (endAt.value ? formatDateTime(endAt.value) : "尚未结束"));
const currentLocationLabel = computed(() => {
  if (session.locationName && session.locationName !== "等待定位") return session.locationName;
  return "等待定位";
});
const visibleOptionalCount = computed(() => contentBlocks.value.length);
const contentBlockSummary = computed(() =>
  contentBlocks.value
    .map((block, index) => {
      const title = block.title.trim() || `图文板块 ${index + 1}`;
      const body = block.body.trim();
      const imageText = block.imageCount ? `图片：${block.imageCount} 张` : "";
      return [title, body, imageText].filter(Boolean).join("\n");
    })
    .filter(Boolean)
    .join("\n\n")
);

function createContentBlock() {
  return {
    id: nextContentBlockId,
    title: "",
    body: "",
    imageCount: 1
  };
}

function addContentBlock() {
  contentBlocks.value = [...contentBlocks.value, createContentBlock()];
  nextContentBlockId += 1;
}

function removeContentBlock(id) {
  contentBlocks.value = contentBlocks.value.filter((block) => block.id !== id);
}

function updateImageCount(block, delta) {
  block.imageCount = Math.min(9, Math.max(0, Number(block.imageCount || 0) + delta));
}

function imageSlots(block) {
  return Array.from({ length: block.imageCount }, (_, index) => `${block.id}-${index}`);
}

function formatDuration(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600).toString().padStart(2, "0");
  const minutes = Math.floor((totalSeconds % 3600) / 60).toString().padStart(2, "0");
  const seconds = Math.floor(totalSeconds % 60).toString().padStart(2, "0");
  return `${hours}:${minutes}:${seconds}`;
}

function formatDateTime(date) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false
  }).format(date);
}

function clearTimer() {
  if (timer.value) {
    window.clearInterval(timer.value);
    timer.value = null;
  }
}

function tick() {
  if (!startAt.value) return;
  elapsedSeconds.value = Math.max(0, Math.floor((Date.now() - startAt.value.getTime()) / 1000));
}

function buildSummary() {
  summaryForm.fishing_spot_name = session.fishingSpotName || session.locationName || "";
  summaryForm.location_name = currentLocationLabel.value;
  summaryForm.latitude = session.latitude;
  summaryForm.longitude = session.longitude;
  summaryForm.weather = weatherName.value;
  summaryForm.temperature = temperatureValue.value;
  summaryForm.fish_count = 0;
  summaryForm.fish_weight = 0;
  summaryForm.fish_species = "";
  summaryForm.fishing_method = "";
  summaryForm.bait = "";
  summaryForm.note = contentBlockSummary.value || session.note;
  summaryForm.images = [];
}

function startFishing() {
  startAt.value = new Date();
  endAt.value = null;
  elapsedSeconds.value = 0;
  savedRecord.value = null;
  status.value = "timing";
  clearTimer();
  timer.value = window.setInterval(tick, 1000);
  emit("action", "开始记录本次钓鱼");
}

function endFishing() {
  if (!startAt.value) return;
  endAt.value = new Date();
  tick();
  clearTimer();
  buildSummary();
  status.value = "summary";
}

function cancelSummary() {
  status.value = "idle";
  startAt.value = null;
  endAt.value = null;
  elapsedSeconds.value = 0;
}

function syncSummaryToSession() {
  session.fishingSpotName = summaryForm.fishing_spot_name;
  session.locationName = summaryForm.location_name;
  session.latitude = summaryForm.latitude;
  session.longitude = summaryForm.longitude;
  session.note = summaryForm.note;
}

function continueEdit() {
  syncSummaryToSession();
  status.value = "review";
}

function reopenSummary() {
  buildSummary();
  status.value = "summary";
}

function handleTimerClick() {
  if (status.value === "timing") {
    endFishing();
    return;
  }
  if (status.value === "saved") {
    resetRecord();
    startFishing();
    return;
  }
  if (status.value === "review") {
    reopenSummary();
    return;
  }
  if (status.value === "idle") {
    startFishing();
  }
}

async function saveRecord() {
  if (!startAt.value || !endAt.value) return;
  saving.value = true;
  const record = {
    user_id: "demo_user",
    start_time: startAt.value.toISOString(),
    end_time: endAt.value.toISOString(),
    duration_seconds: elapsedSeconds.value,
    fishing_spot_name: summaryForm.fishing_spot_name || null,
    location_name: summaryForm.location_name || "未知位置",
    latitude: summaryForm.latitude,
    longitude: summaryForm.longitude,
    weather: summaryForm.weather || null,
    temperature: summaryForm.temperature != null ? Number(summaryForm.temperature) : null,
    fish_count: Number(summaryForm.fish_count) || 0,
    fish_weight: Number(summaryForm.fish_weight) || 0,
    fish_species: summaryForm.fish_species || null,
    fishing_method: summaryForm.fishing_method || null,
    bait: summaryForm.bait || null,
    note: summaryForm.note || null,
    images: summaryForm.images || []
  };
  const created = await createFishingRecord(record);
  saving.value = false;
  savedRecord.value = created;
  status.value = "saved";
  emit("record-saved", created);
  emit("action", created?.offline ? "网络不稳定，记录已保存在当前设备" : "钓鱼记录已保存");
}

function resetRecord() {
  status.value = "idle";
  startAt.value = null;
  endAt.value = null;
  elapsedSeconds.value = 0;
  savedRecord.value = null;
  contentBlocks.value = [];
}

onBeforeUnmount(clearTimer);
</script>

<template>
  <section class="record-page">
    <section class="record-hero card">
      <div class="record-hero-copy">
        <h2>开竿计时</h2>
        <p class="meta">开始计时，补充钓点和现场图文，收竿后生成记录。</p>
      </div>

      <button
        class="record-timer-button"
        :class="{ timing: status === 'timing', review: status === 'review', saved: status === 'saved' }"
        type="button"
        :disabled="status === 'summary'"
        @click="handleTimerClick"
      >
        <span v-if="status === 'timing' || status === 'review'">{{ timerLabel }}</span>
        <span v-else-if="status === 'saved'">已保存</span>
        <span v-else>开始钓鱼</span>
        <small>{{
          status === "timing"
            ? "结束记录"
            : status === "review"
              ? "打开汇总"
              : status === "saved"
                ? "再记一竿"
                : "点击开始计时"
        }}</small>
      </button>

      <p class="record-meta-strip" aria-label="当前钓况">
        <span>{{ weatherName }}</span>
        <span class="record-meta-dot" aria-hidden="true">·</span>
        <span>{{ temperatureValue ?? "--" }}℃</span>
        <span class="record-meta-dot" aria-hidden="true">·</span>
        <span>图文 {{ visibleOptionalCount }} 段</span>
      </p>

      <div class="record-status-grid">
        <div>
          <span>开始时间</span>
          <strong>{{ startTimeLabel }}</strong>
        </div>
        <button type="button" class="record-status-cell" @click="locationPickerOpen = true">
          <span>当前位置</span>
          <span class="record-status-line">
            <strong :class="{ pending: currentLocationLabel === '等待定位' }">{{ currentLocationLabel }}</strong>
            <el-icon class="record-status-chevron" aria-hidden="true"><ArrowRight /></el-icon>
          </span>
        </button>
      </div>

      <button v-if="status === 'saved'" class="btn secondary" type="button" @click="resetRecord">开始新的记录</button>
    </section>

    <RecordLocationDialog
      v-model:open="locationPickerOpen"
      v-model:latitude="session.latitude"
      v-model:longitude="session.longitude"
      v-model:location-name="session.locationName"
      @action="(message) => emit('action', message)"
    />

    <section class="record-addons card">
      <button class="record-add-main" type="button" @click="addContentBlock">
        <span aria-hidden="true"><el-icon><Plus /></el-icon></span>
        <strong>添加图文板块</strong>
        <small>{{ visibleOptionalCount ? `已添加 ${visibleOptionalCount} 个图文板块` : "分段记录鱼情、水情、照片和复盘" }}</small>
      </button>
    </section>

    <section v-if="visibleOptionalCount" class="record-panels">
      <article v-for="(block, index) in contentBlocks" :key="block.id" class="record-panel card text-image-block">
        <div class="record-panel-head">
          <div>
            <h3>图文板块 {{ index + 1 }}</h3>
            <p class="meta">{{ block.imageCount }} 张照片</p>
          </div>
          <button class="mini-btn icon-only" type="button" aria-label="移除图文板块" @click="removeContentBlock(block.id)">
            <el-icon><Delete /></el-icon>
          </button>
        </div>

        <div class="content-field-stack">
          <label class="field">
            <span>标题</span>
            <input v-model="block.title" :placeholder="`例如 第 ${index + 1} 个鱼口窗口`" />
          </label>
          <label class="field">
            <span>正文</span>
            <textarea v-model="block.body" placeholder="记录鱼情、水情、钓法、鱼获或复盘..." />
          </label>
        </div>

        <div class="image-block-editor">
          <div class="record-panel-head image-block-head">
            <span>图片</span>
            <div class="image-count-actions">
              <button class="mini-btn" type="button" :disabled="block.imageCount <= 0" @click="updateImageCount(block, -1)">减少</button>
              <button class="mini-btn" type="button" :disabled="block.imageCount >= 9" @click="updateImageCount(block, 1)">增加</button>
            </div>
          </div>
          <div class="image-placeholder-grid">
            <div v-for="slot in imageSlots(block)" :key="slot" class="image-placeholder">
              <el-icon><Picture /></el-icon>
            </div>
            <button v-if="block.imageCount < 9" class="image-placeholder add-image" type="button" @click="updateImageCount(block, 1)">
              <el-icon><Plus /></el-icon>
            </button>
          </div>
        </div>
      </article>
    </section>

    <div v-if="status === 'summary'" class="record-dialog-backdrop">
      <section class="record-dialog card" role="dialog" aria-modal="true" aria-labelledby="record-dialog-title">
        <div class="dialog-head">
          <h2 id="record-dialog-title">本次钓鱼记录</h2>
          <button class="mini-btn icon-only" type="button" aria-label="关闭" @click="cancelSummary">
            <el-icon><Close /></el-icon>
          </button>
        </div>

        <div class="summary-grid">
          <div><span>开始时间</span><strong>{{ startTimeLabel }}</strong></div>
          <div><span>结束时间</span><strong>{{ endTimeLabel }}</strong></div>
          <div><span>钓鱼时长</span><strong>{{ timerLabel }}</strong></div>
          <div><span>当前定位</span><strong>{{ summaryForm.location_name || "未知位置" }}</strong></div>
          <div><span>位置坐标</span><strong>{{ summaryForm.latitude ?? "--" }}, {{ summaryForm.longitude ?? "--" }}</strong></div>
          <div><span>天气</span><strong>{{ summaryForm.weather || "--" }}</strong></div>
          <div><span>温度</span><strong>{{ summaryForm.temperature ?? "--" }}℃</strong></div>
        </div>

        <form class="form dialog-form" @submit.prevent="saveRecord">
          <div class="catch-grid two">
            <label class="field"><span>钓点名称</span><input v-model="summaryForm.fishing_spot_name" /></label>
            <label class="field"><span>位置名称</span><input v-model="summaryForm.location_name" /></label>
            <label class="field"><span>天气</span><input v-model="summaryForm.weather" /></label>
            <label class="field"><span>温度 ℃</span><input v-model="summaryForm.temperature" step="0.1" type="number" /></label>
          </div>
          <label class="field">
            <span>图文内容汇总</span>
            <textarea v-model="summaryForm.note"></textarea>
          </label>
          <div class="upload-box compact-upload">
            <strong>图文 {{ visibleOptionalCount }} 段</strong>
            <span class="meta">已汇总本次现场记录和照片数量</span>
          </div>

          <div class="dialog-actions">
            <button class="btn secondary" type="button" @click="cancelSummary">取消</button>
            <button class="btn secondary" type="button" @click="continueEdit">继续编辑</button>
            <button class="btn" type="submit" :disabled="saving">{{ saving ? "保存中..." : "保存记录" }}</button>
          </div>
        </form>
      </section>
    </div>
  </section>
</template>
