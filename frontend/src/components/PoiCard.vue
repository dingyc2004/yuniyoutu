<script setup>
defineProps({
  poi: { type: Object, required: true }
});

const emit = defineEmits(["select", "navigate", "detail"]);
</script>

<template>
  <article class="card poi-card clickable" @click="emit('select', poi)">
    <div class="poi-head">
      <div>
        <h3>{{ poi.name }}</h3>
        <p class="meta">{{ poi.type }} · {{ poi.distance }} · {{ (poi.fish || []).join(" / ") }}</p>
      </div>
      <span class="score">{{ poi.score }}</span>
    </div>
    <p class="meta">{{ poi.reason }}</p>
    <p v-if="poi.address" class="meta address">{{ poi.address }}</p>
    <div class="chips compact">
      <span v-for="tag in poi.tags" :key="tag" class="badge">{{ tag }}</span>
    </div>
    <div class="actions">
      <button class="btn" type="button" @click.stop="emit('navigate', poi)">导航</button>
      <button class="btn secondary" type="button" @click.stop="emit('detail', poi)">详情</button>
    </div>
  </article>
</template>
