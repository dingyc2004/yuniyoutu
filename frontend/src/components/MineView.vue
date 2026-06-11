<script setup>
defineProps({
  posts: {
    type: Array,
    default: () => []
  }
});
</script>

<template>
  <section class="card profile-panel">
    <div class="row">
      <div>
        <h2>武汉钓友 008</h2>
        <p class="meta">偏好：野钓、路亚、清晨窗口</p>
      </div>
      <el-tag round type="primary" effect="light">探点官</el-tag>
    </div>
    <div class="stat-grid">
      <div class="stat"><strong>18</strong><span class="meta">出钓</span></div>
      <div class="stat"><strong>6</strong><span class="meta">钓点</span></div>
      <div class="stat"><strong>3.2斤</strong><span class="meta">最大单尾</span></div>
    </div>
  </section>

  <section class="section poi-list">
    <article class="card poi-card">
      <h3>本月报告</h3>
      <p class="meta">你在气温 20-26℃、风力 1-3 级时鱼获率最高。东湖听涛和青山江滩是你的高频点。</p>
      <el-button type="primary" round>生成会员报告</el-button>
    </article>
  </section>

  <section class="section">
    <div class="section-head">
      <h2>我的发布</h2>
      <span class="meta">{{ posts.length }} 条</span>
    </div>
    <div class="mine-post-list">
      <article v-if="!posts.length" class="card poi-card">
        <h3>还没有发布内容</h3>
        <p class="meta">发布图文或视频后，会在这里看到自己的鱼获记录。</p>
      </article>

      <article v-for="post in posts" :key="post.id" class="mine-post-card">
        <div :class="['mine-post-cover', `tone-${post.coverTone || 'blue'}`]">
          <span>{{ post.format }}</span>
        </div>
        <div>
          <h3>{{ post.title }}</h3>
          <p class="meta">{{ post.meta }}</p>
          <div class="chips compact">
            <el-tag round type="info" effect="plain">{{ post.privacy }}</el-tag>
            <el-tag v-if="post.catch" round type="primary" effect="light">{{ post.catch.species }} / {{ post.catch.weight }}</el-tag>
          </div>
        </div>
      </article>
    </div>
  </section>
</template>
