<script setup>
import { reactive } from "vue";

const props = defineProps({
  pois: {
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

function submit() {
  const post = {
    id: `mine_${Date.now()}`,
    format: form.format,
    author: "武汉钓友 008",
    avatar: "我",
    title: form.title,
    excerpt: form.note,
    meta: `${form.poiName || props.pois[0]?.name || "未选择钓点"} · ${form.fishSpecies} · ${form.fishSize} · ${form.fishWeight}`,
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
        <button type="button" :class="{ active: form.format === '图文' }" @click="form.format = '图文'">图文</button>
        <button type="button" :class="{ active: form.format === '视频' }" @click="form.format = '视频'">视频</button>
      </div>

      <div :class="['publish-preview', form.format === '视频' ? 'tone-blue' : 'tone-green']">
        <span>{{ form.format === "视频" ? "短视频封面" : `${form.imageCount} 张图片` }}</span>
        <strong>{{ form.title }}</strong>
      </div>

      <form class="form" @submit.prevent="submit">
        <div class="field">
          <label for="title">标题</label>
          <input id="title" v-model="form.title" />
        </div>

        <div v-if="form.format === '图文'" class="field">
          <label for="image-count">图片数量</label>
          <input id="image-count" v-model="form.imageCount" type="number" min="1" max="9" />
        </div>

        <div class="field">
          <label for="note">正文</label>
          <textarea id="note" v-model="form.note"></textarea>
        </div>

        <div class="catch-grid">
          <div class="field">
            <label for="fish-species">鱼的品种</label>
            <input id="fish-species" v-model="form.fishSpecies" />
          </div>
          <div class="field">
            <label for="fish-size">尺寸</label>
            <input id="fish-size" v-model="form.fishSize" />
          </div>
          <div class="field">
            <label for="fish-weight">重量</label>
            <input id="fish-weight" v-model="form.fishWeight" />
          </div>
        </div>

        <div class="field">
          <label for="poi">定位信息</label>
          <select id="poi" v-model="form.poiName">
            <option value="">不显示具体钓点</option>
            <option v-for="poi in props.pois" :key="poi.id" :value="poi.name">{{ poi.name }}</option>
          </select>
        </div>

        <div class="privacy-row" aria-label="公开方式">
          <button type="button" :class="{ active: form.privacy === '私密' }" @click="form.privacy = '私密'">私密</button>
          <button type="button" :class="{ active: form.privacy === '仅朋友' }" @click="form.privacy = '仅朋友'">仅朋友</button>
          <button type="button" :class="{ active: form.privacy === '公开' }" @click="form.privacy = '公开'">公开</button>
        </div>

        <button class="btn" type="submit">发布</button>
      </form>
    </section>
  </section>
</template>
