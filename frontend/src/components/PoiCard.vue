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
      <span class="score">{{ poi.score }}</span>
    </div>
    <div class="source-row">
      <span class="source-pill">{{ poi.source || "平台整理" }}</span>
      <span class="meta">{{ poi.category || "垂钓点位" }}</span>
    </div>
    <p class="meta">{{ poi.reason }}</p>
    <p v-if="poi.address" class="meta address">{{ poi.address }}</p>

    <div v-if="poi.fish?.length" class="info-block">
      <span class="info-label">鱼种</span>
      <div class="chips compact">
        <button
          v-for="fish in poi.fish"
          :key="fish"
          class="badge fish-badge"
          type="button"
          @click.stop="emit('fish-detail', fish)"
        >
          {{ fish }}
        </button>
      </div>
    </div>

    <div v-if="poi.tags?.length" class="info-block">
      <span class="info-label">标签</span>
      <div class="chips compact">
        <span v-for="tag in poi.tags" :key="tag" class="badge tag-badge">{{ tag }}</span>
      </div>
    </div>

    <div class="actions">
      <button class="btn" type="button" @click.stop="emit('navigate', poi)">导航</button>
      <button class="btn secondary" type="button" @click.stop="emit('detail', poi)">详情</button>
    </div>
  </article>
</template>
