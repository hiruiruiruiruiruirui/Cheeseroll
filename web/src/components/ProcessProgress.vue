<template>
  <div class="card progress-card">
    <div class="status">{{ status }}</div>
    <div class="bar-track">
      <div class="bar-fill" :style="{ width: progress + '%' }"></div>
    </div>
    <div class="percent">{{ progress }}%</div>
  </div>
</template>

<script setup>
defineProps({
  progress: { type: Number, default: 0 },
  status: { type: String, default: '处理中...' },
})
</script>

<style scoped>
.progress-card { text-align: center; }
.status { font-size: 16px; color: #333; margin-bottom: 14px; }
.bar-track {
  height: 10px;
  background: #e8edf2;
  border-radius: 5px;
  overflow: hidden;
  margin-bottom: 8px;
}
.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #1a73e8, #4a9af5);
  border-radius: 5px;
  transition: width 0.5s ease;
}
.percent { font-size: 13px; color: #888; }
</style>
