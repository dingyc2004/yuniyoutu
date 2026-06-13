<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { ArrowLeft, VideoPlay } from "@element-plus/icons-vue";
import { fetchLearningProgress, updateLearningProgress } from "../services/api";

const props = defineProps({
  currentUserId: {
    type: String,
    default: "demo_user"
  },
  tutorials: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(["action"]);
const active = ref("全部");
const filters = ["全部", "图文", "视频", "入门", "进阶"];
const selectedLesson = ref(null);
const progressMap = ref({});

const shown = computed(() => {
  if (active.value === "全部") return props.tutorials;
  return props.tutorials.filter((item) => item.type === active.value || item.level === active.value);
});

function openLesson(lesson) {
  selectedLesson.value = lesson;
  if (!progressMap.value[lesson.id]) setProgress(lesson, "in_progress", false);
}

async function loadProgress() {
  const items = await fetchLearningProgress(props.currentUserId);
  progressMap.value = Object.fromEntries(items.map((item) => [item.tutorial_id, item]));
}

async function setProgress(lesson, status, notify = true) {
  const result = await updateLearningProgress(lesson.id, props.currentUserId, status);
  if (!result) return emit("action", "学习进度保存失败");
  progressMap.value = { ...progressMap.value, [lesson.id]: result };
  if (notify) emit("action", status === "completed" ? `已完成 ${lesson.title}` : `已收藏 ${lesson.title}`);
}

function progressLabel(lesson) {
  return {
    completed: "已完成",
    favorited: "已收藏",
    in_progress: "学习中"
  }[progressMap.value[lesson.id]?.status] || "";
}

onMounted(loadProgress);
watch(() => props.currentUserId, loadProgress);

function renderContent(content) {
  if (!content) return "";
  return content
    .replace(/## (.+)/g, '<h4>$1</h4>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/- (.+)/g, '<li>$1</li>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>');
}
</script>

<template>
  <!-- Lesson Detail -->
  <section v-if="selectedLesson" class="lesson-detail">
    <header class="lesson-detail-header">
      <button class="icon-btn" type="button" @click="selectedLesson = null">
        <el-icon><ArrowLeft /></el-icon>
      </button>
      <div>
        <h2>{{ selectedLesson.title }}</h2>
        <span class="meta">{{ selectedLesson.level }} · {{ selectedLesson.duration }}</span>
      </div>
    </header>

    <div :class="['lesson-detail-cover', `tone-${selectedLesson.coverTone}`]">
      <span class="note-format">
        <el-icon v-if="selectedLesson.type === '视频'"><VideoPlay /></el-icon>
        {{ selectedLesson.type === "视频" ? "视频教程" : "图文教程" }}
      </span>
      <strong>{{ selectedLesson.title }}</strong>
      <div class="chips">
        <el-tag v-for="tag in selectedLesson.tags" :key="tag" round type="primary" effect="light" size="small">{{ tag }}</el-tag>
      </div>
    </div>

    <article class="lesson-detail-body">
      <div v-if="selectedLesson.content" class="lesson-content" v-html="renderContent(selectedLesson.content)"></div>
      <div v-else class="lesson-empty">
        <p>暂无详细内容</p>
        <span class="meta">该教程内容正在整理中，敬请期待。</span>
      </div>
    </article>

    <div class="lesson-detail-actions">
      <el-button round :disabled="progressMap[selectedLesson.id]?.status === 'favorited'" @click="setProgress(selectedLesson, 'favorited')">
        {{ progressMap[selectedLesson.id]?.status === 'favorited' ? "已收藏" : "收藏教程" }}
      </el-button>
      <el-button type="primary" round :disabled="progressMap[selectedLesson.id]?.status === 'completed'" @click="setProgress(selectedLesson, 'completed')">
        {{ progressMap[selectedLesson.id]?.status === 'completed' ? "已完成" : "标记完成" }}
      </el-button>
    </div>
  </section>

  <!-- List -->
  <template v-else>
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
            <span class="meta">{{ progressLabel(lesson) || lesson.type }}</span>
          </div>
          <h3 class="note-title">{{ lesson.title }}</h3>
          <p class="note-excerpt">{{ lesson.summary }}</p>
          <div class="chips compact">
            <el-tag v-for="tag in lesson.tags" :key="tag" round type="primary" effect="light">{{ tag }}</el-tag>
          </div>
          <div class="actions">
            <el-button round :disabled="progressMap[lesson.id]?.status === 'favorited'" @click="setProgress(lesson, 'favorited')">
              {{ progressMap[lesson.id]?.status === 'favorited' ? "已收藏" : "收藏" }}
            </el-button>
            <el-button type="primary" round @click="openLesson(lesson)">开始学习</el-button>
          </div>
        </div>
      </article>
    </section>
  </template>
</template>
