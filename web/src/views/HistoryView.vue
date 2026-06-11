<template>
  <div class="history-layout">
    <!-- Folder Sidebar -->
    <aside class="folder-sidebar">
      <div class="folder-header">
        <h4>📁 资料夹</h4>
        <button class="folder-add-btn" @click="createFolder(null)" title="新建根文件夹">+</button>
      </div>
      <div class="folder-list">
        <div class="folder-item root" :class="{active:activeFolder==='all'}" @click="activeFolder='all';loadRecords()">
          <span class="fi-icon">📋</span> 全部笔记
        </div>
        <div class="folder-item root" :class="{active:activeFolder==='none'}" @click="activeFolder='none';loadRecords()">
          <span class="fi-icon">📂</span> 未分类
        </div>
        <!-- Folder tree -->
        <template v-for="f in folders" :key="f.id">
          <div class="folder-item" :class="{active:activeFolder===f.id}" @click="activeFolder=f.id;loadRecords()">
            <span class="fi-icon">{{ f.children?.length ? '📁' : '📂' }}</span>
            <span class="fi-name">{{ f.name }}</span>
            <small>({{ f.count }})</small>
            <span class="folder-actions">
              <button @click.stop="createFolder(f.id)" title="新建子文件夹">+</button>
              <button @click.stop="startRenameFolder(f)" title="重命名">✏️</button>
              <button @click.stop="deleteFolder(f.id)" title="删除">🗑</button>
            </span>
          </div>
          <!-- Sub-folders (indented) -->
          <div v-if="f.children?.length" class="sub-folders">
            <div v-for="sf in f.children" :key="sf.id" class="folder-item sub" :class="{active:activeFolder===sf.id}" @click="activeFolder=sf.id;loadRecords()">
              <span class="fi-icon">📄</span>
              <span class="fi-name">{{ sf.name }}</span>
              <small>({{ sf.count }})</small>
              <span class="folder-actions">
                <button @click.stop="createFolder(sf.id)" title="新建子文件夹">+</button>
                <button @click.stop="startRenameFolder(sf)" title="重命名">✏️</button>
                <button @click.stop="deleteFolder(sf.id)" title="删除">🗑</button>
              </span>
            </div>
          </div>
        </template>
      </div>
      <div v-if="renamingFolder" class="rename-overlay">
        <input v-model="renameValue" @keyup.enter="confirmRename" @keyup.escape="renamingFolder=null" placeholder="新名称" />
        <button @click="confirmRename">✓</button>
        <button @click="renamingFolder=null">✕</button>
      </div>
    </aside>

    <!-- Records main -->
    <div class="records-main">
      <h2 class="page-title">{{ T.title }}</h2>
      <div v-if="loading" class="state-text">Loading...</div>
      <div v-else-if="!records.length" class="state-empty">
        <span class="empty-icon">📋</span><p>{{ T.empty }}</p>
      </div>
      <div v-else class="record-list">
        <div v-for="r in records" :key="r.id" class="card record-item">
          <div class="ri-main" @click="$router.push(`/result/${r.id}`)">
            <div v-if="editingId===r.id" class="rename-row" @click.stop>
              <input v-model="editTitle" @keyup.enter="saveRename(r.id)" @keyup.escape="editingId=null" class="rename-input" />
              <button class="btn btn-sm btn-primary" @click="saveRename(r.id)">Save</button>
              <button class="btn btn-sm btn-outline" @click="editingId=null">Cancel</button>
            </div>
            <template v-else>
              <span class="title">{{ r.title }}</span>
              <span class="text-sm text-muted">{{ formatDate(r.created_at) }}</span>
            </template>
          </div>
          <div class="ri-actions">
            <span :class="['badge','badge-'+r.status]">{{ r.status==='completed'?T.complete:r.status==='processing'?T.processing:T.failed }}</span>
            <select class="move-select" @change="moveNote(r.id, $event)" title="移动到资料夹">
              <option value="">移动到...</option>
              <option value="none">未分类</option>
              <option v-for="f in flatFolders" :key="f.id" :value="f.id">{{ f.name }}</option>
            </select>
            <button v-if="r.status==='completed'" class="action-btn" @click.stop="startRename(r)">✏️</button>
            <button class="action-btn danger" @click.stop="deleteRecord(r.id)">🗑</button>
          </div>
        </div>
        <div class="pagination" v-if="total>pageSize">
          <button :disabled="page<=1" @click="changePage(-1)" class="btn btn-outline btn-sm">{{ T.prev }}</button>
          <span class="text-sm text-muted">{{ page }} / {{ Math.ceil(total/pageSize) }}</span>
          <button :disabled="page>=Math.ceil(total/pageSize)" @click="changePage(1)" class="btn btn-outline btn-sm">{{ T.next }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../utils/api'
import { t } from '../utils/i18n'

const T = computed(() => t.value.history)
const records = ref([]); const loading = ref(true); const page = ref(1); const total = ref(0); const pageSize = 20
const editingId = ref(null); const editTitle = ref('')
const folders = ref([]); const activeFolder = ref('all')
const renamingFolder = ref(null); const renameValue = ref('')

const flatFolders = computed(() => {
  const result = []
  for (const f of folders.value) {
    result.push(f)
    if (f.children) result.push(...f.children)
  }
  return result
})

onMounted(() => { loadFolders(); loadRecords() })

async function loadFolders() { try { const { data } = await api.get('/folders'); folders.value = data } catch(e){} }
async function loadRecords() {
  loading.value=true
  try { const { data } = await api.get('/records',{params:{page:page.value,page_size:pageSize,folder_id:activeFolder.value}}); records.value=data.items||[]; total.value=data.total }
  catch(e){} finally { loading.value=false }
}
function changePage(d) { page.value+=d; loadRecords() }

async function createFolder(parentId) {
  const name = prompt('新建资料夹名称:')
  if (!name || !name.trim()) return
  try { await api.post('/folders',{name:name.trim(),parent_id:parentId||null}); loadFolders() } catch(e){alert('Failed')}
}
function startRenameFolder(f) { renamingFolder.value = f.id; renameValue.value = f.name }
async function confirmRename() {
  if (!renameValue.value.trim()) return
  try { await api.put(`/folders/${renamingFolder.value}`,{name:renameValue.value.trim()}); loadFolders(); renamingFolder.value = null } catch(e){alert('Failed')}
}
async function deleteFolder(id) { if(!confirm('Delete folder? Notes move to uncategorized.'))return; try { await api.delete(`/folders/${id}`); loadFolders(); loadRecords() } catch(e){} }

async function moveNote(recordId, e) { const fid = e.target.value; if(!fid) return; try { await api.put(`/records/${recordId}/move`,{folder_id: fid==='none'?null:fid}); loadRecords(); loadFolders(); e.target.value='' } catch(e){} }

async function deleteRecord(id) { if(!confirm('Delete permanently?'))return; try { await api.delete(`/records/${id}`); records.value=records.value.filter(r=>r.id!==id); total.value-- } catch(e){alert('Failed')} }
function startRename(r) { editingId.value=r.id; editTitle.value=r.title; }

async function saveRename(id) { if(!editTitle.value.trim())return; try { await api.put(`/records/${id}/rename`,{title:editTitle.value.trim()}); const r=records.value.find(r=>r.id===id); if(r)r.title=editTitle.value.trim(); editingId.value=null } catch(e){alert('Failed')} }
function formatDate(d) { if(!d)return''; const dt=new Date(d); return `${dt.getFullYear()}/${dt.getMonth()+1}/${dt.getDate()}` }
</script>

<style scoped>
.history-layout { display: flex; max-width: 1100px; margin: 0 auto; padding: 24px; gap: 24px; }
.folder-sidebar { width: 220px; flex-shrink: 0; }
.folder-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.folder-header h4 { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0; }
.folder-add-btn { width: 26px; height: 26px; border: 1px solid #e7e5e4; border-radius: 8px; background: #fff; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; color: #d97706; }
.folder-add-btn:hover { background: #fffbeb; border-color: #d97706; }
.folder-list { margin-bottom: 14px; }
.folder-item { display: flex; align-items: center; gap: 4px; padding: 7px 8px; border-radius: 8px; cursor: pointer; font-size: 13px; color: #475569; margin-bottom: 1px; }
.folder-item:hover { background: #f5f5f4; }
.folder-item.active { background: #fef3c7; color: #d97706; font-weight: 600; }
.folder-item.root { font-weight: 500; }
.fi-icon { flex-shrink: 0; }
.fi-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.folder-item small { color: #a8a29e; font-weight: 400; flex-shrink: 0; }
.folder-actions { display: flex; gap: 1px; opacity: 0; transition: opacity 0.15s; flex-shrink: 0; }
.folder-item:hover .folder-actions { opacity: 1; }
.folder-actions button { width: 20px; height: 20px; border: none; background: none; cursor: pointer; font-size: 11px; border-radius: 4px; color: #78716c; }
.folder-actions button:hover { background: #e7e5e4; color: #d97706; }
.sub-folders { padding-left: 12px; border-left: 2px solid #f1f5f9; margin-left: 8px; }
.folder-item.sub { font-size: 12px; padding: 5px 8px; }

.rename-overlay { display: flex; gap: 4px; margin-top: 8px; }
.rename-overlay input { flex: 1; padding: 6px 8px; border: 1px solid #d97706; border-radius: 6px; font-size: 12px; outline: none; }
.rename-overlay button { padding: 4px 8px; border: 1px solid #e7e5e4; border-radius: 6px; background: #fff; cursor: pointer; font-size: 12px; }

.records-main { flex: 1; min-width: 0; }
.page-title { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 20px; }
.state-text { text-align: center; padding: 60px; color: #a8a29e; }
.state-empty { text-align: center; padding: 80px 24px; color: #a8a29e; }
.empty-icon { font-size: 48px; display: block; margin-bottom: 12px; }

.record-item { display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; }
.ri-main { flex: 1; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
.ri-main:hover .title { color: #d97706; }
.title { font-weight: 600; font-size: 15px; color: #0f172a; }
.ri-actions { display: flex; align-items: center; gap: 8px; margin-left: 14px; flex-shrink: 0; }
.badge { font-size: 12px; padding: 2px 10px; border-radius: 20px; font-weight: 500; }
.badge-completed { background: #dcfce7; color: #166534; }
.badge-processing { background: #fef3c7; color: #92400e; }
.badge-failed { background: #fee2e2; color: #991b1b; }
.move-select { font-size: 12px; padding: 2px 6px; border: 1px solid #e7e5e4; border-radius: 6px; color: #78716c; background: #fff; cursor: pointer; max-width: 80px; }
.action-btn { width: 28px; height: 28px; border: 1px solid #e7e5e4; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; display: flex; align-items: center; justify-content: center; }
.action-btn:hover { border-color: #d97706; }
.action-btn.danger:hover { border-color: #dc2626; background: #fef2f2; }
.rename-row { display: flex; gap: 8px; align-items: center; }
.rename-input { flex: 1; padding: 8px 12px; border: 1px solid #d97706; border-radius: 8px; font-size: 14px; outline: none; }
.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; margin-top: 20px; }
@media (max-width: 640px) { .history-layout { flex-direction: column; } .folder-sidebar { width: 100%; } }
</style>
