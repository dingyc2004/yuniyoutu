<script setup>
import { reactive } from "vue";

const props = defineProps({
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
  privacy: "公开",
  imageCount: 3
});

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
  form.imageCount = Math.max(1, Array.isArray(record.images) && record.images.length ? record.images.length : form.imageCount);
  emit("action", "已从记录填充发布信息");
}

function submit() {
  const post = {
    id: `mine_${Date.now()}`,
    format: form.format,
    author: "武汉钓友 008",
    avatar: "我",
    title: form.title,
    content: form.note,
    excerpt: form.note,
    meta: `${form.poiName || props.pois[0]?.name || "未选择钓点"} · ${form.fishSpecies} · ${form.fishSize} · ${form.fishWeight}`,
    postType: form.format === "视频" ? "短视频" : "鱼获分享",
    tags: [`#${form.fishSpecies}`, `#${form.privacy}`, "#鱼获"],
    likes: 0,
    comments: 0,
    saves: 0,
    coverTone: form.format === "视频" ? "blue" : "green",
    imageCount: form.format === "图文" ? Number(form.imageCount) || 1 : 1,
    privacy: form.privacy,
    catch: {
      species: form.fishSpecies,
      size: form.fishSize,
      weight: form.fishWeight,
      location: form.poiName || props.pois[0]?.name || "未选择钓点"
    }
  };
  emit("submit-post", post);
  emit("action", `已发布${form.format}，可见范围：${form.privacy}`);
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

        <div class="privacy-row" aria-label="公开方式">
          <el-segmented v-model="form.privacy" :options="['私密', '仅朋友', '公开']" />
        </div>

        <el-button class="submit-btn" native-type="submit" type="primary" round>发布</el-button>
      </form>
    </section>
  </section>
</template>
