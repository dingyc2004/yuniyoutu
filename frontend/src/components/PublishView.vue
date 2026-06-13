<script setup>
import { reactive, watch } from "vue";
import { createPost } from "../services/api";

const props = defineProps({
  currentUserId: {
    type: String,
    default: "demo_user"
  },
  initialRecord: {
    type: Object,
    default: null
  },
  pois: {
    type: Array,
    default: () => []
  },
  records: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(["action", "submit-post"]);

const form = reactive({
  format: "图文",
  title: "今天这尾鲫鱼状态不错",
  note: "上午口更稳，风小的时候漂相明显，收竿前补了一尾。",
  fishSpecies: "鲫鱼",
  fishSize: "28cm",
  fishWeight: "0.8斤",
  poiName: "",
  contentPrivacy: "public",
  locationPrivacy: "area_blur",
  imageCount: 3,
  recordId: null
});

const contentPrivacyLabel = {
  "public": "公开",
  "friends": "朋友",
  "private": "私密"
};

const locationPrivacyLabel = {
  "precise": "精确位置",
  "area_blur": "水域模糊",
  "city_only": "仅城市",
  "hidden": "完全隐藏"
};

function recordTitle(record) {
  const species = record.fish_species || "钓鱼";
  const spot = record.fishing_spot_name || record.location_name || "未命名钓点";
  return `${spot} · ${species}`;
}

function formatRecordMeta(record) {
  const date = record.start_time ? new Date(record.start_time) : null;
  const dateText = date && !Number.isNaN(date.getTime())
    ? new Intl.DateTimeFormat("zh-CN", { month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false }).format(date)
    : "时间未记录";
  return [
    dateText,
    record.fish_species,
    record.fish_weight ? `${record.fish_weight}斤` : "",
    record.weather
  ].filter(Boolean).join(" · ");
}

function applyRecord(record) {
  if (!record) return;
  const species = record.fish_species || form.fishSpecies;
  const spot = record.fishing_spot_name || record.location_name || "";
  form.title = spot ? `${spot}的${species}鱼获` : `${species}鱼获记录`;
  form.note = record.note || form.note;
  form.fishSpecies = species;
  form.fishWeight = record.fish_weight ? `${record.fish_weight}斤` : form.fishWeight;
  form.fishSize = "";
  form.poiName = spot;
  form.recordId = record.id || null;
  form.imageCount = Math.max(1, Array.isArray(record.images) && record.images.length ? record.images.length : form.imageCount);
  emit("action", "已从记录填充发布信息");
}

watch(() => props.initialRecord, (record) => {
  if (record) applyRecord(record);
}, { immediate: true });

async function submit() {
  const postPayload = {
    user_id: props.currentUserId,
    format: form.format,
    post_type: form.format === "视频" ? "视频" : "鱼获",
    author: "武汉钓友 008",
    avatar: "W",
    title: form.title,
    content: form.note,
    poi_id: null,
    poi_name: form.poiName || null,
    record_id: form.recordId,
    content_type: form.format === "视频" ? "视频" : "鱼获",
    fish_species: form.fishSpecies ? [form.fishSpecies] : [],
    tags: [`#${form.fishSpecies}`, "#鱼获"],
    images: [],
    visibility: form.contentPrivacy,
    location_visibility: form.locationPrivacy,
    location_text: form.poiName || null,
    location_area_name: "武汉市",
    latitude: null,
    longitude: null,
    equipment_ids: []
  };

  const created = await createPost(postPayload);
  if (created) {
    emit("submit-post", created);
    emit("action", `已发布${form.format}，内容:${contentPrivacyLabel[form.contentPrivacy]}，位置:${locationPrivacyLabel[form.locationPrivacy]}`);
  } else {
    emit("action", "发布失败，请检查网络连接");
  }
}
</script>

<template>
  <section class="publish-page">
    <section class="publish-composer">
      <div class="format-switch" aria-label="发布格式">
        <el-segmented v-model="form.format" :options="['图文', '视频']" />
      </div>

      <div :class="['publish-preview', form.format === '视频' ? 'tone-blue' : 'tone-green']">
        <span>{{ form.format === "视频" ? "短视频封面" : `${form.imageCount} 张图片` }}</span>
        <strong>{{ form.title }}</strong>
      </div>

      <section class="record-picker">
        <div class="section-head">
          <h2>从记录快速填充</h2>
          <span class="meta">{{ props.records.length }} 条</span>
        </div>
        <p v-if="!props.records.length" class="meta">还没有可用记录，完成一次钓鱼记录后可在这里一键带入信息。</p>
        <div v-else class="record-picker-list">
          <button
            v-for="record in props.records.slice(0, 4)"
            :key="record.id || record.start_time"
            class="record-picker-item"
            type="button"
            @click="applyRecord(record)"
          >
            <strong>{{ recordTitle(record) }}</strong>
            <span>{{ formatRecordMeta(record) }}</span>
          </button>
        </div>
      </section>

      <form class="form" @submit.prevent="submit">
        <div class="field">
          <label for="title">标题</label>
          <el-input id="title" v-model="form.title" />
        </div>

        <div v-if="form.format === '图文'" class="field">
          <label for="image-count">图片数量</label>
          <el-input-number id="image-count" v-model="form.imageCount" :min="1" :max="9" controls-position="right" />
        </div>

        <div class="field">
          <label for="note">正文</label>
          <el-input id="note" v-model="form.note" type="textarea" :rows="4" />
        </div>

        <div class="catch-grid">
          <div class="field">
            <label for="fish-species">鱼的品种</label>
            <el-input id="fish-species" v-model="form.fishSpecies" />
          </div>
          <div class="field">
            <label for="fish-size">尺寸</label>
            <el-input id="fish-size" v-model="form.fishSize" />
          </div>
          <div class="field">
            <label for="fish-weight">重量</label>
            <el-input id="fish-weight" v-model="form.fishWeight" />
          </div>
        </div>

        <div class="field">
          <label for="poi">定位信息</label>
          <el-select id="poi" v-model="form.poiName" placeholder="不显示具体钓点" clearable>
            <el-option value="" label="不显示具体钓点" />
            <el-option v-for="poi in props.pois" :key="poi.id" :value="poi.name" :label="poi.name" />
          </el-select>
        </div>

        <div class="privacy-row" aria-label="内容可见范围">
          <label>内容可见范围</label>
          <el-segmented v-model="form.contentPrivacy" :options="[
            { label: '公开', value: 'public' },
            { label: '朋友', value: 'friends' },
            { label: '私密', value: 'private' }
          ]" />
        </div>

        <div class="privacy-row" aria-label="位置精度">
          <label>位置精度</label>
          <el-segmented v-model="form.locationPrivacy" :options="[
            { label: '精确', value: 'precise' },
            { label: '水域模糊', value: 'area_blur' },
            { label: '仅城市', value: 'city_only' },
            { label: '隐藏', value: 'hidden' }
          ]" />
        </div>

        <el-button class="submit-btn" native-type="submit" type="primary" round>发布</el-button>
      </form>
    </section>
  </section>
</template>
