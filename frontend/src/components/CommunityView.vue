<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  feed: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(["action"]);
const active = ref("推荐");
const filters = ["推荐", "关注", "同城", "空军", "热门"];

const shown = computed(() => {
  if (active.value === "推荐") return props.feed;

  return props.feed
    .filter((item) => {
      const text = `${item.title} ${item.excerpt} ${item.meta} ${(item.tags || []).join(" ")}`;
      if (active.value === "关注") return ["post_001", "post_002"].includes(item.id);
      if (active.value === "同城") return /武汉|东湖|青山|南湖/.test(text);
      if (active.value === "热门") return item.likes >= 100;
      return text.includes(active.value);
    })
    .sort((a, b) => b.likes - a.likes);
});
</script>

<template>
  <section class="community-hero">
    <div>
      <p class="eyebrow">COMMUNITY</p>
      <h2>图文晒鱼获，视频讲过程</h2>
      <p class="meta">社区支持鱼获、复盘、探点、教程和空军记录。</p>
    </div>
    <div class="community-hero-stats">
      <div><strong>328</strong><span>今日笔记</span></div>
      <div><strong>46</strong><span>视频教程</span></div>
    </div>
  </section>

  <div class="segmented">
    <button v-for="filter in filters" :key="filter" :class="{ active: active === filter }" type="button" @click="active = filter">
      {{ filter }}
    </button>
  </div>

  <section class="feed">
    <article v-for="post in shown" :key="post.id" class="card note-card">
      <div class="note-cover" :class="`tone-${post.coverTone}`">
        <span class="note-format">{{ post.format }}</span>
        <span class="note-score">热度 {{ post.likes }}</span>
      </div>
      <div class="note-body">
        <div class="author-row">
          <div class="avatar">{{ post.avatar }}</div>
          <div>
            <strong>{{ post.author }}</strong>
            <p class="meta">{{ post.meta }}</p>
          </div>
          <button class="follow-btn" type="button" @click="emit('action', `已关注 ${post.author}`)">关注</button>
        </div>
        <h3 class="note-title">{{ post.title }}</h3>
        <p class="note-excerpt">{{ post.excerpt }}</p>
        <div class="chips compact">
          <span v-for="tag in post.tags" :key="tag" class="badge">{{ tag }}</span>
        </div>
        <div class="note-actions">
          <button type="button" @click="emit('action', `喜欢：${post.title}`)">❤ {{ post.likes }}</button>
          <button type="button" @click="emit('action', `评论：${post.title}`)">✎ {{ post.comments }}</button>
          <button type="button" @click="emit('action', `收藏：${post.title}`)">☆ {{ post.saves }}</button>
          <button class="share-action" type="button" @click="emit('action', `分享：${post.title}`)">分享</button>
        </div>
      </div>
    </article>
  </section>
</template>
