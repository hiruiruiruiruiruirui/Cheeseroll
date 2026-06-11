<template>
  <div class="container">
    <div class="page-header">
      <h2>📝 错题本</h2>
      <button class="btn btn-primary btn-sm" @click="showForm = true; editingId = null; resetForm()">+ 添加错题</button>
    </div>

    <!-- Subject filter tabs -->
    <div v-if="subjects.length" class="subject-tabs">
      <span :class="['tab', { active: activeSubject === '' }]" @click="filterSubject('')">全部</span>
      <span
        v-for="s in subjects"
        :key="s"
        :class="['tab', { active: activeSubject === s }]"
        @click="filterSubject(s)"
      >{{ s }}</span>
    </div>

    <!-- States -->
    <div v-if="loading" class="card empty">加载中...</div>
    <div v-else-if="!answers.length" class="card empty">
      <p style="font-size: 40px; margin-bottom: 12px;">📝</p>
      <p>错题本还是空的</p>
      <p class="text-sm text-muted">需要包季度订阅才能使用</p>
    </div>

    <!-- Answers list -->
    <div v-else>
      <p class="summary">共 {{ total }} 道错题</p>
      <div v-for="item in answers" :key="item.id" class="card answer-card">
        <div class="answer-header">
          <span v-if="item.subject" class="answer-subject">{{ item.subject }}</span>
          <span class="answer-date">{{ formatDate(item.created_at) }}</span>
        </div>

        <div class="answer-question">{{ item.question }}</div>

        <div v-if="item.answer || item.correct_answer" class="answer-answer">
          <span class="answer-label">答案：</span>
          {{ item.correct_answer || item.answer }}
        </div>

        <div class="answer-actions">
          <span class="action-link" @click="generateSimilar(item)">🪄 AI 相似题</span>
          <span class="action-link" @click="editItem(item)">✏️ 编辑</span>
          <span class="action-link danger" @click="deleteItem(item.id)">🗑 删除</span>
        </div>
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="total > pageSize">
        <button :disabled="page <= 1" @click="changePage(-1)" class="btn btn-outline btn-sm">上一页</button>
        <span class="text-sm text-muted">{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
        <button :disabled="page >= Math.ceil(total / pageSize)" @click="changePage(1)" class="btn btn-outline btn-sm">下一页</button>
      </div>
    </div>

    <!-- Modal form -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal-card">
        <h3>{{ editingId ? '编辑错题' : '添加错题' }}</h3>

        <div class="form-group">
          <label>科目</label>
          <input v-model="form.subject" class="form-input" placeholder="如：高等数学" />
        </div>

        <div class="form-group">
          <label>题目 *</label>
          <textarea v-model="form.question" class="form-textarea" rows="3" placeholder="输入题目内容..."></textarea>
        </div>

        <div class="form-group">
          <label>我的答案</label>
          <textarea v-model="form.answer" class="form-textarea" rows="2" placeholder="输入你的答案..."></textarea>
        </div>

        <div class="form-group">
          <label>正确答案</label>
          <textarea v-model="form.correct_answer" class="form-textarea" rows="2" placeholder="输入正确答案..."></textarea>
        </div>

        <div class="form-buttons">
          <button class="btn btn-outline" @click="showForm = false">取消</button>
          <button class="btn btn-primary" :disabled="submitting" @click="submitForm">
            {{ submitting ? '提交中...' : editingId ? '保存' : '添加' }}
          </button>
        </div>
      </div>
    </div>

    <!-- AI result modal -->
    <div v-if="showAiResult" class="modal-overlay" @click.self="showAiResult = false">
      <div class="modal-card">
        <h3>🪄 AI 生成相似题</h3>
        <div class="ai-result">
          <p><strong>题目：</strong>{{ aiResult.similar_question }}</p>
          <p v-if="aiResult.answer"><strong>参考答案：</strong>{{ aiResult.answer }}</p>
        </div>
        <div class="form-buttons">
          <button class="btn btn-outline" @click="showAiResult = false">关闭</button>
          <button class="btn btn-primary" :disabled="savingAi" @click="saveAiResult">
            {{ savingAi ? '保存中...' : '保存到错题本' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import api from '../utils/api'

const answers = ref([])
const subjects = ref([])
const activeSubject = ref('')
const loading = ref(true)
const page = ref(1)
const total = ref(0)
const pageSize = 20

// Form state
const showForm = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const form = reactive({ subject: '', question: '', answer: '', correct_answer: '' })

// AI state
const showAiResult = ref(false)
const aiResult = ref({})
const savingAi = ref(false)

onMounted(() => loadAnswers())

function resetForm() {
  form.subject = ''
  form.question = ''
  form.answer = ''
  form.correct_answer = ''
}

async function loadAnswers() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (activeSubject.value) params.subject = activeSubject.value

    const { data } = await api.get('/wrong-answers', { params })
    answers.value = data.items || []
    total.value = data.total

    // Collect unique subjects
    const subjectSet = new Set(subjects.value)
    answers.value.forEach(item => { if (item.subject) subjectSet.add(item.subject) })
    subjects.value = Array.from(subjectSet).sort()
  } catch (e) {
    console.error('Load wrong answers error:', e)
    if (e.response?.status === 402) {
      alert('错题本功能需要包季度订阅')
    }
  } finally {
    loading.value = false
  }
}

function filterSubject(subject) {
  activeSubject.value = subject
  page.value = 1
  loadAnswers()
}

function changePage(delta) {
  page.value += delta
  loadAnswers()
}

function editItem(item) {
  editingId.value = item.id
  form.subject = item.subject || ''
  form.question = item.question
  form.answer = item.answer || ''
  form.correct_answer = item.correct_answer || ''
  showForm.value = true
}

async function submitForm() {
  if (!form.question.trim()) {
    alert('请输入题目')
    return
  }

  submitting.value = true

  try {
    const body = {
      subject: form.subject || null,
      question: form.question,
      answer: form.answer || null,
      correct_answer: form.correct_answer || null,
      tags: [],
    }

    if (editingId.value) {
      await api.put(`/wrong-answers/${editingId.value}`, body)
    } else {
      await api.post('/wrong-answers', body)
    }

    showForm.value = false
    editingId.value = null
    resetForm()
    page.value = 1
    await loadAnswers()
  } catch (e) {
    console.error('Submit error:', e)
    alert(e.response?.data?.detail || '操作失败')
  } finally {
    submitting.value = false
  }
}

async function deleteItem(id) {
  if (!confirm('确定要删除这道错题吗？')) return
  try {
    await api.delete(`/wrong-answers/${id}`)
    page.value = 1
    await loadAnswers()
  } catch (e) {
    alert('删除失败')
  }
}

async function generateSimilar(item) {
  try {
    const { data } = await api.post('/wrong-answers/generate-similar', {
      question: item.question,
      answer: item.answer || item.correct_answer || '',
      subject: item.subject || '',
    })
    aiResult.value = data
    showAiResult.value = true
  } catch (e) {
    console.error('Generate similar error:', e)
    alert(e.response?.data?.detail || 'AI 生成失败')
  }
}

async function saveAiResult() {
  savingAi.value = true
  try {
    await api.post('/wrong-answers', {
      question: aiResult.value.similar_question,
      answer: aiResult.value.answer || '',
      subject: activeSubject.value || null,
      tags: [],
    })
    showAiResult.value = false
    page.value = 1
    await loadAnswers()
  } catch (e) {
    alert('保存失败')
  } finally {
    savingAi.value = false
  }
}

function formatDate(d) {
  if (!d) return ''
  const date = new Date(d)
  return `${date.getMonth() + 1}/${date.getDate()}`
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { margin: 0; }

.summary { font-size: 13px; color: #999; margin-bottom: 12px; }

.subject-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px; }
.tab {
  font-size: 13px; padding: 4px 16px; border-radius: 16px; background: #f0f0f0; color: #666; cursor: pointer;
}
.tab:hover { background: #e0e0e0; }
.tab.active { background: #d97706; color: #fff; }

.answer-card { margin-bottom: 16px; }
.answer-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.answer-subject { font-size: 12px; background: #fef3c7; color: #d97706; padding: 2px 12px; border-radius: 12px; }
.answer-date { font-size: 12px; color: #aaa; }

.answer-question { font-size: 15px; color: #333; line-height: 1.6; margin-bottom: 10px; }
.answer-answer {
  font-size: 14px; color: #555; line-height: 1.5; background: #f8fdf8; padding: 12px; border-radius: 8px; margin-bottom: 10px;
}
.answer-label { font-weight: 600; color: #34a853; }

.answer-actions { display: flex; gap: 20px; padding-top: 10px; border-top: 1px solid #f0f0f0; }
.action-link { font-size: 13px; color: #d97706; cursor: pointer; }
.action-link:hover { text-decoration: underline; }
.action-link.danger { color: #d93025; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 16px; }
.empty { text-align: center; padding: 80px; color: #999; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 24px;
}
.modal-card {
  background: #fff; border-radius: 16px; padding: 32px; width: 100%; max-width: 600px; max-height: 80vh; overflow-y: auto;
}
.modal-card h3 { margin-bottom: 20px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; font-size: 14px; color: #555; margin-bottom: 6px; }
.form-input, .form-textarea {
  width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; box-sizing: border-box;
}
.form-textarea { resize: vertical; }

.form-buttons { display: flex; gap: 12px; margin-top: 20px; }
.form-buttons button { flex: 1; }

.ai-result { background: #f8f9ff; padding: 16px; border-radius: 8px; margin-bottom: 16px; }
.ai-result p { margin-bottom: 8px; line-height: 1.6; }
</style>
