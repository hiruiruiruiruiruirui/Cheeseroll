<template>
  <div class="container">
    <div v-if="loading" class="card" style="text-align:center;padding:60px">加载中...</div>
    <div v-else-if="error" class="card" style="text-align:center;padding:60px;color:#999">{{ error }}</div>
    <template v-else>
      <div class="card">
        <h1>{{ record.title }}</h1>
        <p class="text-sm text-muted">分享自 AI 学习助手</p>
      </div>
      <div class="card">
        <MarkdownViewer :content="record.original_markdown" />
      </div>
      <div class="card cta">
        <p>用 AI 学习助手，上传课件即可自动生成复习笔记</p>
        <button class="btn btn-primary" @click="openApp">打开小程序</button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'
import MarkdownViewer from '../components/MarkdownViewer.vue'

const route = useRoute()
const record = ref({})
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get(`/share/${route.params.code}`)
    record.value = data
  } catch (e) {
    error.value = '笔记不存在或已过期'
  } finally {
    loading.value = false
  }
})

function openApp() {
  alert('请在微信中搜索「AI学习助手」小程序')
}
</script>

<style scoped>
h1 { font-size: 22px; }
.cta { text-align: center; padding: 32px; }
.cta p { color: #888; margin-bottom: 16px; }
</style>
