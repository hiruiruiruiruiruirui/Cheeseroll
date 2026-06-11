<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <img src="/logo.png" alt="芝士卷" class="logo-img" />
        <h1>芝士卷</h1>
      </div>
      <h2>登录</h2>
      <form @submit.prevent="handleLogin" class="auth-form">
        <label>
          <span>邮箱</span>
          <input v-model="email" type="email" placeholder="dev@cheeseroll.com" required />
        </label>
        <label>
          <span>密码</span>
          <input v-model="password" type="password" placeholder="••••••" required />
        </label>
        <div v-if="error" class="auth-error">{{ error }}</div>
        <button type="submit" class="btn-auth" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="auth-switch">
        还没有账号？<router-link to="/register">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true; error.value = ''
  try {
    const { data } = await api.post('/auth/login', { email: email.value, password: password.value })
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('userName', data.user.nickname || 'User')
    userStore.token = data.access_token
    userStore.user = data.user
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || '登录失败'
  } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height: 80vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
.auth-card { width: 100%; max-width: 400px; background: #fff; border: 1px solid #e7e5e4; border-radius: 16px; padding: 40px 32px; }
.auth-logo { display: flex; align-items: center; gap: 10px; justify-content: center; margin-bottom: 24px; }
.logo-img { width: 40px; height: 40px; border-radius: 8px; }
.auth-logo h1 { font-size: 22px; font-weight: 700; color: #1c1917; }
.auth-card h2 { font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 24px; text-align: center; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.auth-form label { display: flex; flex-direction: column; gap: 6px; }
.auth-form label span { font-size: 14px; font-weight: 500; color: #475569; }
.auth-form input { padding: 12px 14px; border: 1px solid #e7e5e4; border-radius: 10px; font-size: 15px; outline: none; }
.auth-form input:focus { border-color: #d97706; }
.auth-error { font-size: 14px; color: #dc2626; }
.btn-auth { padding: 12px; background: #d97706; color: #fff; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; }
.btn-auth:hover { background: #b45309; }
.btn-auth:disabled { opacity: 0.5; cursor: not-allowed; }
.auth-switch { text-align: center; margin-top: 20px; font-size: 14px; color: #a8a29e; }
.auth-switch a { color: #d97706; font-weight: 600; }
</style>
