<script setup>
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import RecordLocationDialog from "./RecordLocationDialog.vue";
import { createFishingRecord } from "../services/api";

const props = defineProps({
  weatherText: { type: String, default: "天气信息暂不可用" },
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

const session = reactive({
  fishingSpotName: "",
  locationName: "等待定位",
  latitude: null,
  longitude: null,
  fishCount: 0,
  fishWeight: 0,
  fishSpecies: "鲫鱼",
  fishingMethod: "台钓",
  bait: "",
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
  summaryForm.fish_count = Number(session.fishCount) || 0;
  summaryForm.fish_weight = Number(session.fishWeight) || 0;
  summaryForm.fish_species = session.fishSpecies;
  summaryForm.fishing_method = session.fishingMethod;
  summaryForm.bait = session.bait;
  summaryForm.note = session.note;
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
  session.fishCount = summaryForm.fish_count;
  session.fishWeight = summaryForm.fish_weight;
  session.fishSpecies = summaryForm.fish_species;
  session.fishingMethod = summaryForm.fishing_method;
  session.bait = summaryForm.bait;
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
  emit("action", created?.offline ? "后端暂不可用，记录已在本地生成" : "钓鱼记录已保存");
}

function resetRecord() {
  status.value = "idle";
  startAt.value = null;
  endAt.value = null;
  elapsedSeconds.value = 0;
  savedRecord.value = null;
}

onBeforeUnmount(clearTimer);
</script>

<template>
  <section class="record-page">
    <section class="record-hero card">
      <p class="eyebrow">FISHING LOG</p>
      <h2>记录</h2>
      <p class="meta">记录本次钓鱼时长、位置与鱼获信息</p>

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

      <div class="record-status-grid">
        <div>
          <span>开始时间</span>
          <strong>{{ startTimeLabel }}</strong>
        </div>
        <button type="button" class="record-status-cell" @click="locationPickerOpen = true">
          <span>当前位置</span>
          <span class="record-status-line">
            <strong :class="{ pending: currentLocationLabel === '等待定位' }">{{ currentLocationLabel }}</strong>
            <span class="record-status-chevron" aria-hidden="true">›</span>
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

    <section class="record-panels">
      <article class="record-panel card">
        <h3>鱼获</h3>
        <div class="catch-grid">
          <label class="field">
            <span>鱼种</span>
            <input v-model="session.fishSpecies" placeholder="例如 鲫鱼" />
          </label>
          <label class="field">
            <span>数量</span>
            <input v-model="session.fishCount" min="0" type="number" />
          </label>
          <label class="field">
            <span>重量/斤</span>
            <input v-model="session.fishWeight" min="0" step="0.1" type="number" />
          </label>
        </div>
      </article>

      <article class="record-panel card">
        <h3>天气</h3>
        <p class="weather-line">{{ weatherName }} · {{ temperatureValue ?? "--" }}℃</p>
        <p class="meta">{{ props.weatherText }}</p>
      </article>

      <article class="record-panel card">
        <h3>备注</h3>
        <div class="catch-grid two">
          <label class="field">
            <span>钓法</span>
            <input v-model="session.fishingMethod" placeholder="台钓 / 路亚" />
          </label>
          <label class="field">
            <span>饵料</span>
            <input v-model="session.bait" placeholder="玉米、蚯蚓、亮片" />
          </label>
        </div>
        <label class="field">
          <span>复盘备注</span>
          <textarea v-model="session.note" placeholder="鱼口、水深、走水、下次改进..."></textarea>
        </label>
      </article>
    </section>

    <div v-if="status === 'summary'" class="record-dialog-backdrop">
      <section class="record-dialog card" role="dialog" aria-modal="true" aria-labelledby="record-dialog-title">
        <div class="dialog-head">
          <div>
            <p class="eyebrow">SUMMARY</p>
            <h2 id="record-dialog-title">本次钓鱼记录</h2>
          </div>
          <button class="mini-btn" type="button" @click="cancelSummary">×</button>
        </div>

        <div class="summary-grid">
          <div><span>开始时间</span><strong>{{ startTimeLabel }}</strong></div>
          <div><span>结束时间</span><strong>{{ endTimeLabel }}</strong></div>
          <div><span>钓鱼时长</span><strong>{{ timerLabel }}</strong></div>
          <div><span>当前定位</span><strong>{{ summaryForm.location_name || "未知位置" }}</strong></div>
          <div><span>经纬度</span><strong>{{ summaryForm.latitude ?? "--" }}, {{ summaryForm.longitude ?? "--" }}</strong></div>
          <div><span>天气</span><strong>{{ summaryForm.weather || "--" }}</strong></div>
          <div><span>温度</span><strong>{{ summaryForm.temperature ?? "--" }}℃</strong></div>
        </div>

        <form class="form dialog-form" @submit.prevent="saveRecord">
          <div class="catch-grid two">
            <label class="field"><span>钓点名称</span><input v-model="summaryForm.fishing_spot_name" /></label>
            <label class="field"><span>位置名称</span><input v-model="summaryForm.location_name" /></label>
            <label class="field"><span>天气</span><input v-model="summaryForm.weather" /></label>
            <label class="field"><span>温度 ℃</span><input v-model="summaryForm.temperature" step="0.1" type="number" /></label>
            <label class="field"><span>鱼获数量</span><input v-model="summaryForm.fish_count" min="0" type="number" /></label>
            <label class="field"><span>鱼获重量/斤</span><input v-model="summaryForm.fish_weight" min="0" step="0.1" type="number" /></label>
            <label class="field"><span>主要鱼种</span><input v-model="summaryForm.fish_species" /></label>
            <label class="field"><span>钓法</span><input v-model="summaryForm.fishing_method" /></label>
            <label class="field"><span>饵料</span><input v-model="summaryForm.bait" /></label>
          </div>
          <label class="field">
            <span>备注</span>
            <textarea v-model="summaryForm.note"></textarea>
          </label>
          <div class="upload-box compact-upload">
            <strong>图片上传入口</strong>
            <span class="meta">MVP 先预留 UI，后续接入相册和文件上传</span>
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
