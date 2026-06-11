<script setup>
import { computed, ref } from "vue";
import { ArrowLeft, Search } from "@element-plus/icons-vue";
import PoiCard from "./PoiCard.vue";

const props = defineProps({
  pois: { type: Array, default: () => [] },
  weatherText: { type: String, default: "天气待更新" }
});

const emit = defineEmits(["search", "action"]);
const selectedPoiId = ref("");
const view = ref("list");
const searchKeyword = ref("");
const rodConnected = ref(false);
const alertLevel = ref("normal");

const selectedPoi = computed(() => props.pois.find((poi) => poi.id === selectedPoiId.value) || props.pois[0]);
const comments = [
  { id: "c1", author: "江风路亚", text: "清晨窗口期更稳定，岸边防滑要注意。" },
  { id: "c2", author: "不空军的阿明", text: "最近小鱼闹窝明显，建议饵料别太腥。" },
  { id: "c3", author: "钓场探路官", text: "停车方便，但周末人多，最好提前出发。" }
];

function selectPoi(poi) {
  selectedPoiId.value = poi.id;
  view.value = "detail";
}

function showRouteNote(poi) {
  selectedPoiId.value = poi.id;
  emit("action", `已选中 ${poi.name}，出发前请确认道路和水域安全`);
}

function toggleRod() {
  rodConnected.value = !rodConnected.value;
  alertLevel.value = rodConnected.value ? "watching" : "normal";
  emit("action", rodConnected.value ? "智能鱼竿已连接" : "智能鱼竿已断开");
}

function simulateBite() {
  if (!rodConnected.value) {
    emit("action", "请先连接智能鱼竿");
    return;
  }
  alertLevel.value = "bite";
  emit("action", "咬饵预警：竿尖震动异常");
}
</script>

<template>
  <section class="fishing-view">
    <template v-if="view === 'list'">
      <section class="fishing-entry-grid">
        <button class="fishing-entry active" type="button">
          <strong>钓点</strong>
          <span>查看附近钓点和钓友评论</span>
        </button>
        <button class="fishing-entry" type="button" @click="view = 'rod'">
          <strong>智能鱼竿</strong>
          <span>查看竿尖状态和水下动态</span>
        </button>
      </section>

      <form class="home-search" @submit.prevent="emit('search', searchKeyword)">
        <el-icon aria-hidden="true"><Search /></el-icon>
        <el-input v-model="searchKeyword" type="search" placeholder="搜索水库、河流、钓场" clearable />
        <el-button native-type="submit" type="primary" round>搜索</el-button>
      </form>

      <section class="section poi-list fishing-pois">
        <article class="fish-intro">
          <h2>先选钓点，再开始出钓</h2>
          <p>结合距离、鱼种、风险提示和钓友反馈，挑一个更适合今天的点位。</p>
        </article>
        <PoiCard
          v-for="poi in props.pois"
          :key="poi.id"
          :poi="poi"
          @select="selectPoi"
          @navigate="showRouteNote"
          @detail="selectPoi"
          @fish-detail="(fish) => emit('action', `查看鱼种：${fish}`)"
        />
      </section>
    </template>

    <template v-else-if="view === 'detail' && selectedPoi">
      <el-button text class="back-link" :icon="ArrowLeft" @click="view = 'list'">返回钓点</el-button>

      <article class="spot-detail">
        <div class="spot-cover tone-blue">
          <span>{{ selectedPoi.type }}</span>
          <strong>{{ selectedPoi.name }}</strong>
        </div>
        <div class="spot-body">
          <div class="poi-head">
            <div>
              <h2>{{ selectedPoi.name }}</h2>
              <p class="meta">{{ selectedPoi.distance }} · {{ props.weatherText }}</p>
            </div>
            <el-tag class="score" round effect="dark">{{ selectedPoi.score }}</el-tag>
          </div>
          <p class="spot-copy">{{ selectedPoi.reason }}</p>
          <p class="meta">{{ selectedPoi.address }}</p>

          <div v-if="selectedPoi.fish?.length" class="chips compact">
            <el-tag v-for="fish in selectedPoi.fish" :key="fish" round type="success" effect="light">{{ fish }}</el-tag>
          </div>

          <section class="detail-section">
            <h4>图文信息</h4>
            <p>{{ selectedPoi.risk }}</p>
          </section>

          <section class="detail-section">
            <h4>钓友评论</h4>
            <div class="comment-list">
              <div v-for="comment in comments" :key="comment.id" class="comment-item">
                <strong>{{ comment.author }}</strong>
                <p>{{ comment.text }}</p>
              </div>
            </div>
          </section>
        </div>
      </article>

      <div class="trip-actions">
        <el-button type="primary" round @click="showRouteNote(selectedPoi)">确认钓点</el-button>
        <el-button round @click="view = 'list'">继续看钓点</el-button>
      </div>
    </template>

    <template v-else>
      <el-button text class="back-link" :icon="ArrowLeft" @click="view = 'list'">返回我要钓鱼</el-button>

      <section class="smart-rod-page">
        <div>
          <h2>智能鱼竿连接</h2>
          <p class="meta">到达钓点后查看竿尖状态、水下动态和咬饵提醒。</p>
        </div>

        <div class="rod-camera" :class="alertLevel">
          <span class="scan-line"></span>
          <div class="fish-shadow one"></div>
          <div class="fish-shadow two"></div>
          <strong>{{ rodConnected ? "水下实时画面" : "等待连接智能鱼竿" }}</strong>
          <p>{{ rodConnected ? "摄像头、竿尖传感器、震动预警在线" : "连接后展示鱼竿附近水下情况" }}</p>
        </div>

        <div class="rod-status">
          <div>
            <span>咬饵状态</span>
            <strong>{{ alertLevel === "bite" ? "强烈预警" : rodConnected ? "持续监测" : "未连接" }}</strong>
          </div>
          <div>
            <span>水下能见度</span>
            <strong>{{ rodConnected ? "良好" : "--" }}</strong>
          </div>
        </div>
        <div class="trip-actions">
          <el-button type="primary" round @click="toggleRod">{{ rodConnected ? "断开鱼竿" : "连接智能鱼竿" }}</el-button>
          <el-button round @click="simulateBite">测试提醒</el-button>
        </div>
      </section>
    </template>
  </section>
</template>
