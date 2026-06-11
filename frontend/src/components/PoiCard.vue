<script setup>
defineProps({
  poi: { type: Object, required: true }
});

const emit = defineEmits(["select", "navigate", "detail", "fish-detail"]);
</script>

<template>
  <article class="card poi-card clickable" @click="emit('select', poi)">
    <div class="poi-head">
      <div>
        <h3>{{ poi.name }}</h3>
        <p class="meta">{{ poi.type }} · {{ poi.distance }}</p>
      </div>
      <el-tag class="score" round effect="dark">{{ poi.score }}</el-tag>
    </div>
    <div class="source-row">
      <el-tag class="source-pill" round type="info" effect="plain">{{ poi.source || "平台整理" }}</el-tag>
      <span class="meta">{{ poi.category || "垂钓点位" }}</span>
    </div>
    <p class="meta">{{ poi.reason }}</p>
    <p v-if="poi.address" class="meta address">{{ poi.address }}</p>

    <div v-if="poi.fish?.length" class="info-block">
      <span class="info-label">鱼种</span>
      <div class="chips compact">
        <el-tag
          v-for="fish in poi.fish"
          :key="fish"
          class="badge fish-badge"
          round
          type="success"
          effect="light"
          @click.stop="emit('fish-detail', fish)"
        >
          {{ fish }}
        </el-tag>
      </div>
    </div>

    <div v-if="poi.tags?.length" class="info-block">
      <span class="info-label">标签</span>
      <div class="chips compact">
        <el-tag v-for="tag in poi.tags" :key="tag" round type="primary" effect="light">{{ tag }}</el-tag>
      </div>
    </div>

    <div class="actions">
      <el-button type="primary" round @click.stop="emit('navigate', poi)">导航</el-button>
      <el-button round @click.stop="emit('detail', poi)">详情</el-button>
    </div>
  </article>
</template>
