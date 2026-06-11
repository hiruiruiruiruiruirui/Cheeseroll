<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-badge"><span class="dot"></span> {{ T.badge }}</div>
      <h1>{{ T.title1 }}<br /><span class="gradient-text">{{ T.title2 }}</span></h1>
      <p class="hero-sub">{{ T.subtitle }}</p>
      <div class="hero-btns">
        <button v-if="!isLoggedIn" class="btn btn-solid" @click="devLogin" :disabled="loginLoading">
          {{ loginLoading ? '...' : T.cta }} <span class="arrow">→</span>
        </button>
        <span v-else class="ready-text">{{ T.ready }}</span>
      </div>
    </section>

    <!-- Upload Zone + Detail Settings -->
    <section class="upload-section">
      <!-- Detail level selector (visible to logged-in users) -->
      <div v-if="isLoggedIn" class="settings-card">
        <div class="settings-header">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          <span>{{ Td.title }}</span>
        </div>

        <!-- Note detail level (always visible) -->
        <div class="detail-label">{{ Td.noteLevel }}</div>
        <div class="detail-options">
          <label class="detail-opt" :class="{ active: noteDetailLevel === 'brief' }">
            <input type="radio" v-model="noteDetailLevel" value="brief" />
            <div class="do-content">
              <strong>{{ Td.brief }}</strong>
              <span>{{ Td.briefDesc }}</span>
            </div>
          </label>
          <label class="detail-opt" :class="{ active: noteDetailLevel === 'default' }">
            <input type="radio" v-model="noteDetailLevel" value="default" />
            <div class="do-content">
              <strong>{{ Td.default }}</strong>
              <span>{{ Td.defaultDesc }}</span>
            </div>
          </label>
          <label class="detail-opt" :class="{ active: noteDetailLevel === 'detailed' }">
            <input type="radio" v-model="noteDetailLevel" value="detailed" />
            <div class="do-content">
              <strong>{{ Td.detailed }}</strong>
              <span>{{ Td.detailedDesc }}</span>
            </div>
          </label>
        </div>

        <!-- Broadcast mode toggle -->
        <div class="broadcast-row">
          <div class="broadcast-info">
            <span class="broadcast-icon">🎙️</span>
            <div>
              <strong>{{ Td.broadcast }}</strong>
              <span>{{ Td.broadcastDesc }}</span>
            </div>
          </div>
          <label class="toggle-switch">
            <input type="checkbox" v-model="broadcastMode" />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <!-- Broadcast detail level (shown when broadcast is ON) -->
        <transition name="fade">
        <div class="detail-options" v-if="broadcastMode">
          <div class="detail-label">{{ Td.broadcastStyle }}</div>
          <label class="detail-opt" :class="{ active: broadcastLevel === 'brief' }">
            <input type="radio" v-model="broadcastLevel" value="brief" />
            <div class="do-content">
              <strong>{{ Td.styleBrief }}</strong>
              <span>{{ Td.styleBriefDesc }}</span>
            </div>
          </label>
          <label class="detail-opt" :class="{ active: broadcastLevel === 'default' }">
            <input type="radio" v-model="broadcastLevel" value="default" />
            <div class="do-content">
              <strong>{{ Td.styleDefault }}</strong>
              <span>{{ Td.styleDefaultDesc }}</span>
            </div>
          </label>
          <label class="detail-opt" :class="{ active: broadcastLevel === 'detailed' }">
            <input type="radio" v-model="broadcastLevel" value="detailed" />
            <div class="do-content">
              <strong>{{ Td.styleDetailed }}</strong>
              <span>{{ Td.styleDetailedDesc }}</span>
            </div>
          </label>
        </div>
        </transition>

        <!-- Custom notes -->
        <div class="notes-section">
          <label class="notes-label">{{ Td.notes }}</label>
          <textarea v-model="customNotes" :placeholder="Td.notesPlaceholder" rows="2" @input="saveNotes"></textarea>
          <div class="notes-history" v-if="notesHistory.length">
            <span class="nh-label">{{ Td.notesHint }}</span>
            <div class="nh-tags">
              <span v-for="(n, i) in notesHistory" :key="i" class="nh-tag" @click="customNotes = n; saveNotes()">{{ n.slice(0, 40) }}{{ n.length > 40 ? '...' : '' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Dropzone -->
      <div class="upload-card" :class="{ active: dragging }"
        @click="triggerUpload"
        @dragover.prevent="dragging=true" @dragleave.prevent="dragging=false" @drop.prevent="handleDrop">
        <input ref="fileInput" type="file" accept=".pptx,.docx,.pdf" @change="handleFileSelect" :disabled="isProcessing" hidden />
        <div class="upload-visual">
          <div class="upload-icon-wrap">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
          </div>
          <div class="upload-text">
            <h4>{{ uploadedFileName || T.dropHere }}</h4>
            <p>{{ T.dropHint }}</p>
          </div>
        </div>
        <div v-if="uploadError" class="upload-err">{{ uploadError }}</div>
      </div>

      <!-- Progress -->
      <div v-if="isProcessing" class="progress-card">
        <div class="progress-info">
          <span class="progress-label">{{ statusText }}</span>
          <span class="progress-pct">{{ progress }}%</span>
        </div>
        <div class="progress-track"><div class="progress-fill" :style="{ width: progress + '%' }"></div></div>
      </div>
    </section>

    <!-- Recent Records -->
    <section v-if="recentRecords.length && isLoggedIn" class="records">
      <div class="section-label">RECENT</div>
      <h2>{{ T.recent }}</h2>
      <div class="record-grid">
        <div v-for="r in recentRecords" :key="r.id" class="record-card" @click="$router.push(`/result/${r.id}`)">
          <div class="rc-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          </div>
          <div class="rc-body">
            <div class="rc-title">{{ r.title }}</div>
            <div class="rc-meta">
              <span :class="['rc-badge', r.status==='completed'?'ok':r.status==='processing'?'warn':'fail']">
                {{ r.status === 'completed' ? T.complete : r.status === 'processing' ? T.processing : T.failed }}
              </span>
              <span class="rc-date">{{ formatDate(r.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How it Works -->
    <section class="how">
      <div class="section-label">HOW IT WORKS</div>
      <h2>{{ T.howTitle }}</h2>
      <div class="steps">
        <div class="step"><div class="step-num">1</div><h4>{{ T.step1Title }}</h4><p>{{ T.step1Desc }}</p></div>
        <div class="step-arrow">→</div>
        <div class="step"><div class="step-num">2</div><h4>{{ T.step2Title }}</h4><p>{{ T.step2Desc }}</p></div>
        <div class="step-arrow">→</div>
        <div class="step"><div class="step-num">3</div><h4>{{ T.step3Title }}</h4><p>{{ T.step3Desc }}</p></div>
        <div class="step-arrow">→</div>
        <div class="step"><div class="step-num">4</div><h4>{{ T.step4Title }}</h4><p>{{ T.step4Desc }}</p></div>
      </div>
    </section>

    <!-- Features -->
    <section class="suite">
      <div class="section-label">FEATURES</div>
      <h2>{{ T.featuresTitle }}</h2>
      <div class="suite-grid">
        <div class="suite-card"><div class="sc-icon-wrap cheese"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></div>
          <h4>{{ T.feat1Title }}</h4><p>{{ T.feat1Desc }}</p><span class="sc-tag live">{{ T.live }}</span></div>
        <div class="suite-card"><div class="sc-icon-wrap amber"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><line x1="8" y1="2" x2="8" y2="4"/><line x1="16" y1="2" x2="16" y2="4"/></svg></div>
          <h4>{{ T.feat2Title }}</h4><p>{{ T.feat2Desc }}</p><span class="sc-tag soon">{{ T.soon }}</span></div>
        <div class="suite-card"><div class="sc-icon-wrap green"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></div>
          <h4>{{ T.feat3Title }}</h4><p>{{ T.feat3Desc }}</p><span class="sc-tag soon">{{ T.soon }}</span></div>
        <div class="suite-card"><div class="sc-icon-wrap purple"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></div>
          <h4>{{ T.feat4Title }}</h4><p>{{ T.feat4Desc }}</p><span class="sc-tag live">{{ T.live }}</span></div>
        <div class="suite-card"><div class="sc-icon-wrap rose"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg></div>
          <h4>{{ T.feat5Title }}</h4><p>{{ T.feat5Desc }}</p><span class="sc-tag live">{{ T.live }}</span></div>
        <div class="suite-card"><div class="sc-icon-wrap teal"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg></div>
          <h4>{{ T.feat6Title }}</h4><p>{{ T.feat6Desc }}</p><span class="sc-tag soon">{{ T.soon }}</span></div>
      </div>
    </section>

    <section class="trust"><p class="trust-text" v-html="T.trust"></p></section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import { t } from '../utils/i18n'

const router = useRouter()
const userStore = useUserStore()
const T = computed(() => t.value.home)
const Td = computed(() => t.value.detail)

const fileInput = ref(null)
const dragging = ref(false)
const isProcessing = ref(false)
const progress = ref(0)
const statusText = ref('')
const fileId = ref(null)
const recentRecords = ref([])
const isLoggedIn = ref(!!localStorage.getItem('token'))
const loginLoading = ref(false)
const uploadedFileName = ref('')
const uploadError = ref('')
let pollingTimer = null

// Detail settings
const noteDetailLevel = ref(localStorage.getItem('noteDetailLevel') || 'default')
const broadcastMode = ref(localStorage.getItem('broadcastMode') === 'true')
const broadcastLevel = ref(localStorage.getItem('broadcastLevel') || 'default')
const customNotes = ref('')
const notesHistory = ref(JSON.parse(localStorage.getItem('notesHistory') || '[]'))

watch(noteDetailLevel, v => localStorage.setItem('noteDetailLevel', v))
watch(broadcastMode, v => localStorage.setItem('broadcastMode', v))
watch(broadcastLevel, v => localStorage.setItem('broadcastLevel', v))

function saveNotes() {
  if (customNotes.value.trim()) {
    const h = notesHistory.value.filter(n => n !== customNotes.value)
    h.unshift(customNotes.value)
    if (h.length > 10) h.pop()
    notesHistory.value = h
    localStorage.setItem('notesHistory', JSON.stringify(h))
  }
}

onMounted(() => { if (isLoggedIn.value) loadRecentRecords() })

function triggerUpload() {
  if (!isLoggedIn.value) { router.push('/login'); return }
  if (!isProcessing.value) fileInput.value?.click()
}
function handleDrop(e) {
  dragging.value = false
  if (!isLoggedIn.value) { router.push('/login'); return }
  const f = e.dataTransfer?.files?.[0]; if (f) uploadFile(f)
}
function handleFileSelect(e) {
  if (!isLoggedIn.value) { router.push('/login'); return }
  const f = e.target?.files?.[0]; if (f) uploadFile(f)
}

async function uploadFile(file) {
  uploadError.value = ''
  const ext = file.name.split('.').pop()?.toLowerCase()
  if (!['pptx','docx','pdf'].includes(ext)) { uploadError.value = 'Unsupported format. Use .pptx, .docx, or .pdf'; return }
  if (file.size > 50*1024*1024) { uploadError.value = `File too large (${(file.size/1024/1024).toFixed(1)}MB)`; return }
  uploadedFileName.value = file.name
  const fd = new FormData(); fd.append('file', file)
  try {
    const { data } = await api.post('/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    fileId.value = data.file_id; await startProcessing()
  } catch (e) {
    if (e.response?.status === 402) { router.push('/plans'); return }
    uploadError.value = e.response?.data?.detail || 'Upload failed'
  }
}

async function devLogin() {
  loginLoading.value = true
  try {
    const { data } = await api.post('/auth/dev-login')
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('userName', data.user.nickname || 'User')
    userStore.token = data.access_token; userStore.user = data.user
    isLoggedIn.value = true; loadRecentRecords()
  } catch (e) { alert('Login failed') } finally { loginLoading.value = false }
}

async function startProcessing() {
  isProcessing.value = true; progress.value = 5; statusText.value = T.value.queued
  try {
    const { data } = await api.post('/process', {
      file_id: fileId.value,
      detail_level: noteDetailLevel.value,
      custom_notes: customNotes.value,
    })
    // Store broadcast pref for result page
    if (broadcastMode.value) {
      localStorage.setItem('broadcastActive', 'true')
      localStorage.setItem('broadcastLevel', broadcastLevel.value)
    } else {
      localStorage.removeItem('broadcastActive')
    }
    startPolling(data.task_id)
  } catch (e) {
    isProcessing.value = false
    if (e.response?.status === 402) { router.push('/plans'); return }
    uploadError.value = 'Processing failed: ' + (e.response?.data?.detail || e.message)
  }
}

function startPolling(taskId) {
  if (pollingTimer) clearInterval(pollingTimer)
  const map = { queued:[5,T.value.queued], parsing:[20,T.value.parsing], generating:[60,T.value.generating], exporting:[90,T.value.exporting], completed:[100,T.value.complete], failed:[0,T.value.failed] }
  pollingTimer = setInterval(async () => {
    try {
      const { data } = await api.get(`/process/${taskId}/status`)
      const [p, t] = map[data.status] || [0, data.status]
      progress.value = p; statusText.value = t
      if (data.status === 'completed' && data.record_id) { clearInterval(pollingTimer); setTimeout(() => { isProcessing.value = false; router.push(`/result/${data.record_id}`) }, 600) }
      else if (data.status === 'failed') { clearInterval(pollingTimer); isProcessing.value = false; uploadError.value = data.error_message || 'Processing failed' }
    } catch (e) {}
  }, 2000)
}

async function loadRecentRecords() {
  try { const { data } = await api.get('/records', { params: { page: 1, page_size: 3 } }); recentRecords.value = data.items || [] } catch (e) {}
}

function formatDate(d) { if (!d) return ''; const dt = new Date(d); return `${dt.getMonth()+1}/${dt.getDate()} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}` }
</script>

<style scoped>
.home { max-width: 1100px; margin: 0 auto; padding: 0 32px 100px; }

.hero { text-align: center; padding: 72px 0 48px; }
.hero-badge { display: inline-flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; letter-spacing: 0.08em; color: #92400e; text-transform: uppercase; margin-bottom: 28px; background: #fef3c7; padding: 5px 16px; border-radius: 20px; }
.dot { width: 6px; height: 6px; background: #d97706; border-radius: 50%; }
.hero h1 { font-size: 48px; font-weight: 800; line-height: 1.15; color: #0f172a; letter-spacing: -0.03em; margin-bottom: 16px; }
.gradient-text { background: linear-gradient(135deg, #d97706, #ea580c); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub { font-size: 17px; color: #64748b; line-height: 1.7; max-width: 640px; margin: 0 auto 32px; }
.hero-btns { display: flex; justify-content: center; }
.btn-solid { display: inline-flex; align-items: center; gap: 8px; padding: 14px 36px; font-size: 16px; font-weight: 600; background: #d97706; color: #fff; border: none; border-radius: 12px; cursor: pointer; transition: all 0.15s; }
.btn-solid:hover { background: #b45309; transform: translateY(-1px); box-shadow: 0 8px 24px rgba(217,119,6,0.25); }
.btn-solid:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }
.arrow { font-size: 20px; }
.ready-text { color: #16a34a; font-weight: 600; font-size: 16px; }

.upload-section { max-width: 680px; margin: 0 auto 56px; }

/* Settings card */
.settings-card { background: #fff; border: 1px solid #e7e5e4; border-radius: 14px; padding: 24px; margin-bottom: 18px; }
.settings-header { display: flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #78716c; margin-bottom: 18px; }
.detail-label { font-size: 13px; font-weight: 600; color: #78716c; margin-bottom: 10px; }
.detail-options { display: flex; gap: 10px; margin-bottom: 18px; }
.detail-opt { flex: 1; display: flex; padding: 14px; border: 2px solid #e7e5e4; border-radius: 10px; cursor: pointer; transition: all 0.15s; }
.detail-opt:hover { border-color: #d4d1c9; }
.detail-opt.active { border-color: #d97706; background: #fffbeb; }
.detail-opt input { display: none; }
.do-content strong { display: block; font-size: 14px; color: #292524; margin-bottom: 4px; }
.do-content span { font-size: 12px; color: #a8a29e; line-height: 1.4; }
.notes-section { border-top: 1px solid #f1f5f9; padding-top: 16px; }
.notes-label { font-size: 13px; font-weight: 600; color: #78716c; display: block; margin-bottom: 8px; }
.notes-section textarea { width: 100%; padding: 10px 14px; border: 1px solid #e7e5e4; border-radius: 10px; font-size: 14px; font-family: inherit; resize: vertical; outline: none; color: #292524; }
.notes-section textarea:focus { border-color: #d97706; }
.notes-history { margin-top: 10px; }
.nh-label { font-size: 11px; color: #a8a29e; display: block; margin-bottom: 6px; }
.nh-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.nh-tag { font-size: 12px; padding: 3px 10px; background: #f5f5f4; border-radius: 8px; color: #78716c; cursor: pointer; transition: background 0.15s; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.nh-tag:hover { background: #fef3c7; color: #92400e; }

/* Upload card */
.upload-card { border: 2px dashed #cbd5e1; border-radius: 16px; padding: 44px 32px; text-align: center; cursor: pointer; transition: all 0.15s; background: #f8fafc; }
.upload-card:hover, .upload-card.active { border-color: #d97706; background: #fffbeb; }
.upload-visual { display: flex; align-items: center; justify-content: center; gap: 16px; }
.upload-icon-wrap { width: 56px; height: 56px; border-radius: 14px; background: #fed7aa; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.upload-text { text-align: left; }
.upload-text h4 { font-size: 17px; font-weight: 600; color: #0f172a; margin-bottom: 4px; }
.upload-text p { font-size: 14px; color: #94a3b8; }
.upload-err { margin-top: 16px; font-size: 14px; color: #dc2626; }

.progress-card { margin-top: 16px; padding: 20px 24px; background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; }
.progress-info { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; }
.progress-label { color: #475569; font-weight: 500; }
.progress-pct { color: #d97706; font-weight: 600; }
.progress-track { height: 6px; background: #e2e8f0; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: #d97706; border-radius: 3px; transition: width 0.4s; }

.how { text-align: center; padding: 64px 0; border-top: 1px solid #f1f5f9; }
.section-label { font-size: 11px; font-weight: 700; letter-spacing: 0.12em; color: #d97706; margin-bottom: 12px; }
.how h2, .records h2, .suite h2 { font-size: 28px; font-weight: 700; color: #0f172a; letter-spacing: -0.02em; margin-bottom: 40px; }
.steps { display: flex; align-items: flex-start; justify-content: center; gap: 12px; flex-wrap: wrap; }
.step { flex: 1; min-width: 180px; max-width: 220px; text-align: center; }
.step-num { width: 40px; height: 40px; border-radius: 12px; background: #fef3c7; color: #d97706; font-weight: 700; font-size: 18px; display: flex; align-items: center; justify-content: center; margin: 0 auto 14px; }
.step h4 { font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 6px; }
.step p { font-size: 14px; color: #64748b; line-height: 1.5; }
.step-arrow { color: #cbd5e1; font-size: 24px; margin-top: 8px; }
@media (max-width: 768px) { .step-arrow { display: none; } .detail-options { flex-direction: column; } }

.records { text-align: center; padding: 64px 0; border-top: 1px solid #f1f5f9; }
.record-grid { display: flex; flex-direction: column; gap: 10px; max-width: 640px; margin: 0 auto; }
.record-card { display: flex; align-items: center; gap: 16px; padding: 18px 22px; background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; cursor: pointer; text-align: left; transition: border-color 0.15s; }
.record-card:hover { border-color: #d97706; }
.rc-icon { flex-shrink: 0; }
.rc-body { flex: 1; }
.rc-title { font-size: 15px; font-weight: 600; color: #0f172a; margin-bottom: 6px; }
.rc-meta { display: flex; align-items: center; gap: 12px; }
.rc-badge { font-size: 11px; font-weight: 600; padding: 2px 10px; border-radius: 8px; }
.rc-badge.ok { background: #dcfce7; color: #166534; }
.rc-badge.warn { background: #fef3c7; color: #92400e; }
.rc-badge.fail { background: #fee2e2; color: #991b1b; }
.rc-date { font-size: 13px; color: #94a3b8; }

.suite { text-align: center; padding: 64px 0; border-top: 1px solid #f1f5f9; }
.suite-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
@media (max-width: 768px) { .suite-grid { grid-template-columns: 1fr; } }
.suite-card { position: relative; text-align: left; padding: 28px 24px; background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; transition: all 0.15s; }
.suite-card:hover { border-color: #cbd5e1; box-shadow: 0 4px 16px rgba(0,0,0,0.04); }
.sc-icon-wrap { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 18px; }
.sc-icon-wrap.cheese { background: #fef3c7; color: #d97706; }
.sc-icon-wrap.amber { background: #fffbeb; color: #d97706; }
.sc-icon-wrap.green { background: #f0fdf4; color: #16a34a; }
.sc-icon-wrap.purple { background: #f5f3ff; color: #7c3aed; }
.sc-icon-wrap.rose { background: #fff1f2; color: #e11d48; }
.sc-icon-wrap.teal { background: #f0fdfa; color: #0d9488; }
.suite-card h4 { font-size: 16px; font-weight: 600; color: #0f172a; margin-bottom: 8px; }
.suite-card p { font-size: 14px; color: #64748b; line-height: 1.55; }
.sc-tag { position: absolute; top: 20px; right: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.04em; padding: 3px 10px; border-radius: 8px; text-transform: uppercase; }
.sc-tag.live { background: #dcfce7; color: #166534; }
.sc-tag.soon { background: #f1f5f9; color: #64748b; }

/* Broadcast toggle */
.broadcast-row { display: flex; align-items: center; justify-content: space-between; padding: 16px 0; border-bottom: 1px solid #f1f5f9; margin-bottom: 16px; }
.broadcast-info { display: flex; align-items: center; gap: 10px; }
.broadcast-icon { font-size: 24px; }
.broadcast-info strong { display: block; font-size: 14px; color: #292524; }
.broadcast-info span { font-size: 12px; color: #a8a29e; }
.toggle-switch { position: relative; width: 48px; height: 28px; cursor: pointer; flex-shrink: 0; }
.toggle-switch input { display: none; }
.toggle-slider { position: absolute; inset: 0; background: #d6d3d1; border-radius: 14px; transition: 0.2s; }
.toggle-slider::before { content: ''; position: absolute; top: 3px; left: 3px; width: 22px; height: 22px; background: #fff; border-radius: 50%; transition: 0.2s; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
.toggle-switch input:checked + .toggle-slider { background: #d97706; }
.toggle-switch input:checked + .toggle-slider::before { transform: translateX(20px); }

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s, max-height 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; max-height: 0; overflow: hidden; }
.fade-enter-to, .fade-leave-from { opacity: 1; max-height: 300px; }

/* Voice Player */
.player-card {
  margin-top: 18px; padding: 20px; background: #fff; border: 1px solid #e7e5e4; border-radius: 14px;
}
.player-header { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.player-icon { font-size: 28px; }
.player-info strong { display: block; font-size: 14px; color: #292524; }
.player-info span { font-size: 12px; color: #d97706; font-weight: 500; }
.player-controls { display: flex; align-items: center; gap: 10px; }
.player-btn { width: 36px; height: 36px; border-radius: 10px; border: 1px solid #e7e5e4; background: #fff; cursor: pointer; font-size: 14px; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.player-btn:hover { border-color: #d97706; background: #fffbeb; }
.player-progress-wrap { flex: 1; display: flex; align-items: center; gap: 10px; }
.player-progress-track { flex: 1; height: 6px; background: #e7e5e4; border-radius: 3px; overflow: hidden; }
.player-progress-fill { height: 100%; background: #d97706; border-radius: 3px; transition: width 0.2s; }
.player-time { font-size: 12px; color: #a8a29e; min-width: 36px; text-align: right; font-variant-numeric: tabular-nums; }

.trust { text-align: center; padding: 48px 0; border-top: 1px solid #f1f5f9; }
.trust-text { font-size: 15px; color: #94a3b8; }
.trust-text :deep(strong) { color: #475569; }
</style>
