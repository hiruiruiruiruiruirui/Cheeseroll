<template>
  <div class="container">
    <h2>{{ Tm.title }}</h2>

    <div class="card profile-card">
      <div class="avatar">🧀</div>
      <div class="profile-info">
        <div class="nickname">{{ userName }}</div>
        <div class="text-sm text-muted">{{ user?.email || Tm.unbound }}</div>
      </div>
    </div>

    <div class="card">
      <div class="menu-item" @click="$router.push('/history')"><span>📋 {{ Tm.myNotes }}</span><span>→</span></div>
      <div class="menu-item" @click="$router.push('/wrong-answers')"><span>📝 {{ Tm.wrongBook }}</span><span>→</span></div>
      <div class="menu-item" @click="$router.push('/plans')"><span>💎 {{ Tm.subscription }}</span><span>→</span></div>
    </div>

    <button class="btn btn-outline" style="width:100%" @click="showLogout = true">{{ Tm.logout }}</button>

    <div v-if="showLogout" class="modal-overlay" @click.self="showLogout = false">
      <div class="modal-card">
        <h3>{{ Tm.confirmLogout }}</h3>
        <p>{{ Tm.logoutMsg }}</p>
        <div class="modal-btns">
          <button class="btn-cancel" @click="showLogout = false">{{ Tm.cancel || 'Cancel' }}</button>
          <button class="btn-confirm" @click="confirmLogout">{{ Tm.confirmLogout }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import { useUserStore } from '../stores/user'
import { t } from '../utils/i18n'

const router = useRouter()
const userStore = useUserStore()
const user = ref(null)
const showLogout = ref(false)
const userName = ref(localStorage.getItem('userName') || 'User')
const Tm = computed(() => t.value.mine)

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/me')
    user.value = data
    userName.value = data.nickname || 'User'
  } catch (e) {}
})

function confirmLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  userStore.token = null; userStore.user = null
  showLogout.value = false; router.push('/')
}
</script>

<style scoped>
h2 { font-size: 22px; font-weight: 700; color: #0f172a; margin-bottom: 20px; }
.profile-card { display: flex; align-items: center; gap: 16px; }
.avatar { font-size: 44px; width: 56px; height: 56px; display: flex; align-items: center; justify-content: center; background: #fef3c7; border-radius: 14px; }
.nickname { font-size: 18px; font-weight: 600; color: #0f172a; }

.menu-item { display: flex; justify-content: space-between; padding: 14px 0; border-bottom: 1px solid #f1f5f9; cursor: pointer; font-size: 15px; color: #292524; }
.menu-item:last-child { border-bottom: none; }
.menu-item:hover { color: #d97706; }

.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 24px; }
.modal-card { background: #fff; border-radius: 16px; padding: 32px; max-width: 400px; width: 100%; }
.modal-card h3 { font-size: 18px; font-weight: 700; margin-bottom: 12px; }
.modal-card p { font-size: 14px; color: #78716c; line-height: 1.6; margin-bottom: 24px; }
.modal-btns { display: flex; gap: 12px; }
.btn-cancel { flex: 1; padding: 10px; border: 1px solid #e7e5e4; border-radius: 10px; background: #fff; color: #78716c; font-size: 15px; cursor: pointer; }
.btn-confirm { flex: 1; padding: 10px; border: none; border-radius: 10px; background: #d97706; color: #fff; font-size: 15px; font-weight: 600; cursor: pointer; }
</style>
