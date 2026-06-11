<template>
  <div
    class="upload-zone"
    :class="{ dragging, disabled }"
    @dragover.prevent="dragging = true"
    @dragleave.prevent="dragging = false"
    @drop.prevent="handleDrop"
  >
    <input
      ref="fileInput"
      type="file"
      accept=".pptx,.docx,.pdf"
      @change="handleFileChange"
      :disabled="disabled"
      hidden
    />
    <div class="upload-content" @click="!disabled && $refs.fileInput.click()">
      <div class="upload-icon">🧀</div>
      <div class="upload-text">
        {{ disabled ? '处理中...' : dragging ? '松开上传' : '点击或拖拽文件到此处上传' }}
      </div>
      <div class="upload-hint">支持 .pptx / .docx / .pdf（最大 50MB）</div>
      <div v-if="error" class="upload-error">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../utils/api'

const emit = defineEmits(['uploaded'])
defineProps({ disabled: { type: Boolean, default: false } })

const fileInput = ref(null)
const dragging = ref(false)
const error = ref('')

const MAX_SIZE = 50 * 1024 * 1024
const ALLOWED = ['pptx', 'docx', 'pdf']

async function uploadFile(file) {
  error.value = ''

  const ext = file.name.split('.').pop().toLowerCase()
  if (!ALLOWED.includes(ext)) {
    error.value = `不支持的文件格式: .${ext}`
    return
  }
  if (file.size > MAX_SIZE) {
    error.value = `文件过大: ${(file.size / 1024 / 1024).toFixed(1)}MB (最大 50MB)`
    return
  }

  const formData = new FormData()
  formData.append('file', file)

  try {
    const { data } = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    emit('uploaded', data.file_id)
  } catch (e) {
    error.value = e.response?.data?.detail || '上传失败'
  }
}

function handleDrop(e) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) uploadFile(file)
}

function handleFileChange(e) {
  const file = e.target?.files?.[0]
  if (file) uploadFile(file)
}
</script>

<style scoped>
.upload-zone {
  border: 2px dashed #E0D8C4;
  border-radius: 16px;
  background: #FFFDF7;
  cursor: pointer;
  transition: all 0.2s;
}
.upload-zone:hover,
.upload-zone.dragging {
  background: var(--cheese-light);
  border-color: var(--cheese-gold);
}
.upload-zone.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.upload-content {
  text-align: center;
  padding: 60px 24px;
}
.upload-icon { font-size: 64px; margin-bottom: 12px; }
.upload-text {
  font-size: 18px;
  color: var(--dark);
  font-weight: 600;
  margin-bottom: 8px;
}
.upload-hint { font-size: 14px; color: var(--muted); }
.upload-error {
  margin-top: 12px;
  color: #e53935;
  font-size: 14px;
}
</style>
