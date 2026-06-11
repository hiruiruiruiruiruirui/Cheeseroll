<template>
  <div class="result-layout">
    <!-- Main content -->
    <div class="result-main">
      <div v-if="loading" class="state">Loading...</div>
      <div v-else-if="error" class="state"><p>{{ error }}</p><button class="btn btn-primary mt-16" @click="loadRecord">Retry</button></div>
      <template v-else>
        <!-- Header -->
        <div class="card">
          <h1 class="record-title">{{ record.title }}</h1>
          <div class="flex-between mt-16">
            <span class="text-sm text-muted">{{ formatDate(record.created_at) }}</span>
            <div style="display:flex;gap:8px">
              <button v-if="record.status==='completed'" class="btn btn-primary btn-sm" @click="downloadPdf" :disabled="downloading">{{ downloading?'Preparing...':'📥 PDF' }}</button>
              <button class="btn btn-outline btn-sm" @click="shareRecord">🔗 Share</button>
            </div>
          </div>
        </div>

        <!-- Voice Player -->
        <div v-if="broadcastActive" class="player-card">
          <div class="pl-hdr"><span>🎙️</span><span>{{ Tr.voice }} · {{ broadcastLabel }}</span></div>
          <div class="pl-ctrl">
            <button class="pbtn" @click="togglePlay">{{ isSpeaking?'⏸':'▶️' }}</button>
            <button class="pbtn" @click="stopPlay">⏹</button>
            <div class="pprogress"><span class="ptime">{{ voiceElapsed }}</span><div class="ptrack"><div class="pfill" :style="{width:voiceProgress+'%'}"></div></div><span class="ptime">{{ voiceDuration }}</span></div>
          </div>
        </div>

        <!-- Markdown with text selection -->
        <div class="card md-card" @mouseup="handleTextSelect">
          <MarkdownViewer :content="record.original_markdown" />
        </div>

      </template>
    </div>

    <!-- AI Assistant Sidebar -->
    <aside class="assistant-sidebar" :class="{ open: sidebarOpen }">
      <button class="as-toggle" @click="sidebarOpen=!sidebarOpen">{{ sidebarOpen ? '✕' : Tr.aiTutor }}</button>
      <div v-if="sidebarOpen" class="as-content">
        <h4>🧀 {{ Tr.aiAssistant }}</h4>
        <div v-if="selectedText" class="as-selected">
          <div class="as-text">"{{ selectedText.slice(0, 200) }}{{ selectedText.length>200?'...':'' }}"</div>
          <div class="as-actions">
            <button class="as-btn" @click="askAI('translate')" :disabled="asLoading">🌐 {{ Tr.translate }}</button>
            <button class="as-btn" @click="askAI('explain')" :disabled="asLoading">💡 {{ Tr.explain }}</button>
            <button class="as-btn" @click="askAI('takeaways')" :disabled="asLoading">🔑 {{ Tr.takeaways }}</button>
          </div>
        </div>
        <div v-else class="as-hint">{{ Tr.selectHint }}</div>
        <div v-if="asResult" class="as-result">{{ asResult }}</div>
        <div v-if="asLoading" class="as-loading">Thinking...</div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../utils/api'
import { t } from '../utils/i18n'
import MarkdownViewer from '../components/MarkdownViewer.vue'

const route = useRoute()
const record = ref({})
const loading = ref(true)
const error = ref('')
const downloading = ref(false)
const Tr = computed(() => t.value.result)

// Voice
const broadcastActive = ref(localStorage.getItem('broadcastActive')==='true')
const broadcastLevel = ref(localStorage.getItem('broadcastLevel')||'default')
const broadcastLabel = computed(() => {
  const labels = { brief: Tr.value.brief, default: Tr.value.default, detailed: Tr.value.detailed }
  return labels[broadcastLevel.value] || Tr.value.default
})
const isSpeaking = ref(false); const isPaused = ref(false)
const voiceProgress = ref(0); const voiceElapsed = ref('0:00'); const voiceDuration = ref('0:00')
let synth=null, utterance=null, interval=null

// AI Assistant
const sidebarOpen = ref(false)
const selectedText = ref('')
const asLoading = ref(false)
const asResult = ref('')


onMounted(()=>{ if(route.params.id) loadRecord(); else { loading.value=false; error.value='Missing note ID' } })
onUnmounted(()=>stopPlay())

async function loadRecord() {
  loading.value=true; error.value=''
  try {
    const { data } = await api.get(`/records/${route.params.id}`)
    record.value = data
    if(broadcastActive.value && data.original_markdown) setTimeout(()=>startPlay(data.original_markdown),500)
  } catch(e) { error.value = e.response?.data?.detail||'Failed to load' } finally { loading.value=false }
}

// Text selection
function handleTextSelect() {
  const sel = window.getSelection()?.toString()?.trim()
  if(sel && sel.length > 5) { selectedText.value = sel; asResult.value = '' }
}

async function askAI(action) {
  if(!selectedText.value) return
  asLoading.value = true; asResult.value = ''
  const prompts = {
    translate: `Translate the following text to ${/[一-鿿]/.test(selectedText.value)?'English':'Chinese'}. Only return the translation:\n\n${selectedText.value}`,
    explain: `Explain the following concept in simple terms. Keep it concise (2-3 sentences):\n\n${selectedText.value}`,
    takeaways: `Give me 3 key takeaways from this content in bullet points:\n\n${selectedText.value}`
  }
  try {
    const { data } = await api.post('/process/ask-ai', { prompt: prompts[action] || prompts.explain })
    asResult.value = data.result
  } catch(e) { asResult.value = 'Failed to get response' }
  finally { asLoading.value = false }
}

// Voice — language detection + natural voice selection
let voiceLoaded = false
let availableVoices = []
window.speechSynthesis?.addEventListener('voiceschanged', () => { availableVoices = speechSynthesis.getVoices(); voiceLoaded = true })
// Preload
setTimeout(() => { if (window.speechSynthesis) { availableVoices = speechSynthesis.getVoices(); voiceLoaded = true } }, 200)

function detectDocLang(md) { if(!md) return 'zh-CN'; const chinese = [...md].filter(c => c >= '一' && c <= '鿿').length; const total = md.replace(/\s/g,'').length || 1; return chinese/total > 0.3 ? 'zh-CN' : 'en-US' }

function getBestVoice(lang) {
  const voices = availableVoices.length ? availableVoices : speechSynthesis.getVoices()
  const langPrefix = lang.slice(0,2)
  const matches = voices.filter(v => v.lang.startsWith(langPrefix))
  if (!matches.length) return null
  const preferred = langPrefix === 'zh'
    ? ['Google','Tingting','Huihui','Microsoft']
    : ['Google','Samantha','Microsoft David','Microsoft Zira','Apple','Karen']
  for (const p of preferred) { const found = matches.find(v => v.name.toLowerCase().includes(p.toLowerCase())); if (found) return found }
  return matches[0]
}

function stripMarkdown(md) { if(!md) return ''; return md.replace(/^#{1,6}\s/gm,'').replace(/\*\*(.+?)\*\*/g,'$1').replace(/\*(.+?)\*/g,'$1').replace(/`{1,3}[^`]*`{1,3}/g,'').replace(/\$\$?[^$]+\$\$?/g,'').replace(/\[([^\]]+)\]\([^)]+\)/g,'$1').replace(/<[^>]+>/g,'').replace(/\n{2,}/g,'. ').replace(/\n/g,' ').replace(/\s+/g,' ').trim() }
function getPlaybackText() { const raw=record.value?.original_markdown||''; const text=stripMarkdown(raw); const intro=Tr.value.intro + (record.value?.title||'') + '。'; return intro+text }

function startPlay(text) {
  if(!window.speechSynthesis)return; stopPlay()
  synth=window.speechSynthesis; utterance=new SpeechSynthesisUtterance(text)
  utterance.rate=0.95; utterance.pitch=1.0
  const docLang = detectDocLang(record.value?.original_markdown||'')
  const uiLang = (localStorage.getItem('lang')||'zh-CN').startsWith('en') ? 'en-US' : 'zh-CN'
  const lang = uiLang // Follow UI language setting
  utterance.lang = lang
  const voice = getBestVoice(lang)
  if (voice) utterance.voice = voice
  console.log('Voice:', lang, voice?.name||'default')
  voiceDuration.value=`${Math.round(text.length/240)}:${String(Math.round(text.length/4)%60).padStart(2,'0')}`
  utterance.onboundary=e=>{if(utterance?.text){voiceProgress.value=Math.round((e.charIndex/utterance.text.length)*100); voiceElapsed.value=`${Math.round(e.charIndex/240)}:${String(Math.round(e.charIndex/4)%60).padStart(2,'0')}`}}
  utterance.onend=()=>{isSpeaking.value=false;voiceProgress.value=100}
  synth.speak(utterance); isSpeaking.value=true
}
function togglePlay() { if(isSpeaking.value){synth.pause();isSpeaking.value=false}else if(isPaused.value){synth.resume();isSpeaking.value=true}else startPlay(getPlaybackText()) }
function stopPlay() { if(synth){synth.cancel();isSpeaking.value=false;voiceProgress.value=0;voiceElapsed.value='0:00'} }

async function downloadPdf() {
  downloading.value=true
  try {
    const res = await api.get(`/records/${route.params.id}/pdf`, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data)
    const a = document.createElement('a'); a.href = url; a.download = `${record.value.title||'notes'}.pdf`; a.click()
    URL.revokeObjectURL(url)
  }
  catch(e) { alert('PDF not available yet - try processing a new document') }
  finally { downloading.value=false }
}
function shareRecord() {
  const url = record.value.share_code?`${window.location.origin}/share/${record.value.share_code}`:window.location.href
  navigator.clipboard?.writeText(url).then(()=>alert('Link copied!')).catch(()=>alert('Share: '+url))
}
function formatDate(d) { if(!d)return''; const dt=new Date(d); return `${dt.getFullYear()}/${dt.getMonth()+1}/${dt.getDate()} ${String(dt.getHours()).padStart(2,'0')}:${String(dt.getMinutes()).padStart(2,'0')}` }
</script>

<style scoped>
.result-layout { display: flex; min-height: calc(100vh - 60px); max-width: 1400px; margin: 0 auto; }
.result-main { flex: 1; padding: 24px; min-width: 0; }
.record-title { font-size: 22px; font-weight: 600; color: #0f172a; }
.state { text-align: center; padding: 80px 24px; color: #a8a29e; }

/* Voice Player */
.player-card { padding: 16px 20px; background: #fff; border: 1px solid #e7e5e4; border-radius: 14px; margin-bottom: 16px; }
.pl-hdr { display: flex; align-items: center; gap: 8px; font-size: 14px; color: #78716c; margin-bottom: 10px; }
.pl-ctrl { display: flex; align-items: center; gap: 8px; }
.pbtn { width: 32px; height: 32px; border-radius: 8px; border: 1px solid #e7e5e4; background: #fff; cursor: pointer; }
.pprogress { flex: 1; display: flex; align-items: center; gap: 8px; }
.ptrack { flex: 1; height: 4px; background: #e7e5e4; border-radius: 2px; overflow: hidden; }
.pfill { height: 100%; background: #d97706; border-radius: 2px; }
.ptime { font-size: 11px; color: #a8a29e; min-width: 32px; }

/* AI Assistant */
.assistant-sidebar { position: sticky; top: 60px; height: calc(100vh - 60px); background: #fafaf9; border-left: 1px solid #e7e5e4; transition: width 0.2s; width: 80px; flex-shrink: 0; }
.assistant-sidebar.open { width: 320px; }
.as-toggle { width: auto; padding: 6px 12px; height: 36px; border: 1px solid #d97706; background: #fffbeb; cursor: pointer; font-size: 12px; font-weight: 600; color: #d97706; display: flex; align-items: center; justify-content: center; border-radius: 8px; position: absolute; top: 16px; right: 8px; white-space: nowrap; }
.as-toggle:hover { background: #fef3c7; border-color: #d97706; }
.as-content { padding: 20px; overflow-y: auto; height: 100%; }
.as-content h4 { font-size: 16px; font-weight: 700; color: #0f172a; margin-bottom: 16px; }
.as-selected { margin-bottom: 16px; }
.as-text { font-size: 13px; color: #78716c; background: #f5f5f4; padding: 10px; border-radius: 8px; margin-bottom: 10px; font-style: italic; line-height: 1.5; }
.as-actions { display: flex; flex-direction: column; gap: 6px; }
.as-btn { padding: 10px 14px; background: #fff; border: 1px solid #e7e5e4; border-radius: 10px; font-size: 13px; cursor: pointer; text-align: left; transition: all 0.15s; }
.as-btn:hover { border-color: #d97706; background: #fffbeb; }
.as-btn:disabled { opacity: 0.5; }
.as-hint { font-size: 13px; color: #a8a29e; line-height: 1.6; }
.as-result { margin-top: 16px; padding: 14px; background: #fff; border: 1px solid #e7e5e4; border-radius: 10px; font-size: 14px; color: #292524; line-height: 1.6; white-space: pre-wrap; }
.as-loading { margin-top: 16px; font-size: 13px; color: #d97706; }

.md-card { cursor: default; }
</style>
