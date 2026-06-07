<script setup>
import { computed, ref } from "vue";
import PoiCard from "./PoiCard.vue";

const props = defineProps({
  pois: { type: Array, default: () => [] },
  weatherText: { type: String, default: "天气信息暂不可用" }
});

const emit = defineEmits(["search", "action"]);
const selectedPoiId = ref("");
const view = ref("list");
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
  emit("action", "后续会接入跳转高德 APP 导航，不再在应用内渲染高德地图");
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
          <span>连接硬件、查看水下画面</span>
        </button>
      </section>

      <form class="home-search" @submit.prevent="(event) => emit('search', event.target.elements.keyword.value)">
        <span aria-hidden="true">⌕</span>
        <input name="keyword" type="search" placeholder="搜索水库、河流、钓场" />
        <button type="submit">搜索</button>
      </form>

      <section class="section poi-list fishing-pois">
        <article class="fish-intro">
          <p class="eyebrow">FISHING SPOTS</p>
          <h2>先选钓点，再开始出钓</h2>
          <p>当前版本只展示钓点列表和详情。导航后续改为跳转高德 APP，不再使用高德 API 在页面内可视化地图。</p>
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
      <button class="back-link" type="button" @click="view = 'list'">‹ 返回钓点</button>

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
            <span class="score">{{ selectedPoi.score }}</span>
          </div>
          <p class="spot-copy">{{ selectedPoi.reason }}</p>
          <p class="meta">{{ selectedPoi.address }}</p>

          <div v-if="selectedPoi.fish?.length" class="chips compact">
            <span v-for="fish in selectedPoi.fish" :key="fish" class="badge fish-badge">{{ fish }}</span>
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
        <button class="btn" type="button" @click="showRouteNote(selectedPoi)">导航说明</button>
        <button class="btn secondary" type="button" @click="view = 'list'">继续看钓点</button>
      </div>
    </template>

    <template v-else>
      <button class="back-link" type="button" @click="view = 'list'">‹ 返回我要钓鱼</button>

      <section class="smart-rod-page">
        <div>
          <p class="eyebrow">SMART ROD</p>
          <h2>智能鱼竿连接</h2>
          <p class="meta">到达钓点后连接硬件，查看水下画面并接收咬饵预警。</p>
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
          <button class="btn" type="button" @click="toggleRod">{{ rodConnected ? "断开鱼竿" : "连接智能鱼竿" }}</button>
          <button class="btn secondary" type="button" @click="simulateBite">模拟咬饵</button>
        </div>
      </section>
    </template>
  </section>
</template>
