<script setup>
defineProps({
  pois: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(["action"]);

function submit() {
  emit("action", "已生成鱼获战绩卡，位置按隐私设置展示");
}
</script>

<template>
  <section class="card poi-card">
    <div class="upload-box">
      <div>
        <strong>上传鱼获照片或空军现场</strong>
        <p class="meta">自动绑定天气、时间和钓点，便于后续复盘。</p>
      </div>
    </div>

    <form class="form" @submit.prevent="submit">
      <div class="field">
        <label for="catch-type">记录类型</label>
        <select id="catch-type">
          <option>鱼获</option>
          <option>空军</option>
          <option>探点</option>
        </select>
      </div>

      <div class="field">
        <label for="poi">钓点</label>
        <select id="poi">
          <option v-for="poi in pois" :key="poi.id">{{ poi.name }}</option>
        </select>
      </div>

      <div class="field">
        <label for="fish">鱼种</label>
        <input id="fish" value="鲫鱼、翘嘴" />
      </div>

      <div class="field">
        <label for="method">钓法</label>
        <select id="method">
          <option>台钓</option>
          <option>路亚</option>
          <option>海钓</option>
          <option>夜钓</option>
        </select>
      </div>

      <div class="field">
        <label for="privacy">位置隐私</label>
        <select id="privacy">
          <option>模糊公开 1km</option>
          <option>精确公开</option>
          <option>仅互关可见</option>
          <option>完全隐藏</option>
        </select>
      </div>

      <div class="field">
        <label for="note">心得</label>
        <textarea id="note">上午口更稳，风小的时候漂相明显。</textarea>
      </div>

      <button class="btn" type="submit">生成鱼获战绩卡</button>
    </form>
  </section>
</template>
