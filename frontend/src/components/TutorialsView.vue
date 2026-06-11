<script setup>
import { computed, ref } from "vue";
import { VideoPlay } from "@element-plus/icons-vue";

const props = defineProps({
  tutorials: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(["action"]);
const active = ref("全部");
const filters = ["全部", "图文", "视频", "入门", "进阶"];

const shown = computed(() => {
  if (active.value === "全部") return props.tutorials;
  return props.tutorials.filter((item) => item.type === active.value || item.level === active.value);
});
</script>

<template>
  <section class="tutorial-hero">
    <div>
      <h2>图文能讲步骤，视频能看动作</h2>
      <p class="meta">教程按新手路径拆成可收藏、可复盘的练习单元。</p>
    </div>
    <div class="tutorial-path">
      <span>能不能钓</span>
      <span>怎么找点</span>
      <span>怎么复盘</span>
    </div>
  </section>

  <el-segmented v-model="active" class="segmented" :options="filters" />

  <section class="lesson-list">
    <article v-for="lesson in shown" :key="lesson.id" class="card lesson-card">
      <div class="lesson-cover" :class="`tone-${lesson.coverTone}`">
        <span class="note-format">
          <el-icon v-if="lesson.type === '视频'"><VideoPlay /></el-icon>
          {{ lesson.type === "视频" ? "视频" : "图文" }}
        </span>
        <span class="note-score">{{ lesson.level }}</span>
      </div>
      <div class="note-body">
        <div class="row">
          <el-tag round type="info" effect="plain">{{ lesson.duration }}</el-tag>
          <span class="meta">{{ lesson.type }}</span>
        </div>
        <h3 class="note-title">{{ lesson.title }}</h3>
        <p class="note-excerpt">{{ lesson.summary }}</p>
        <div class="chips compact">
          <el-tag v-for="tag in lesson.tags" :key="tag" round type="primary" effect="light">{{ tag }}</el-tag>
        </div>
        <div class="actions">
          <el-button round @click="emit('action', `已收藏 ${lesson.title}`)">收藏</el-button>
          <el-button type="primary" round @click="emit('action', `开始学习 ${lesson.title}`)">开始学习</el-button>
        </div>
      </div>
    </article>
  </section>
</template>
