<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <img src="/logo.png" alt="芝士卷" class="logo-img" />
        <h1>芝士卷</h1>
      </div>
      <h2>注册</h2>
      <form @submit.prevent="handleRegister" class="auth-form">
        <label>
          <span>昵称</span>
          <input v-model="nickname" type="text" placeholder="你的昵称" />
        </label>
        <label>
          <span>邮箱</span>
          <input v-model="email" type="email" placeholder="your@email.com" required />
        </label>
        <label>
          <span>密码</span>
          <input v-model="password" type="password" placeholder="至少6位" required minlength="6" />
        </label>
        <label>
          <span>验证码</span>
          <div class="code-row">
            <input v-model="verifyCode" type="text" placeholder="6位验证码" required maxlength="6" />
            <button type="button" class="btn-code" @click="sendCode" :disabled="codeSending || countdown > 0">
              {{ countdown > 0 ? `${countdown}s` : codeSending ? '发送中...' : '获取验证码' }}
            </button>
          </div>
        </label>
        <div v-if="error" class="auth-error">{{ error }}</div>
        <div v-if="codeSent" class="auth-ok">验证码：<strong>{{ devCode }}</strong>（开发模式直接显示）</div>
        <button type="submit" class="btn-auth" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>
      <p class="auth-switch">
        已有账号？<router-link to="/login">登录</router-link>
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
const nickname = ref('')
const email = ref('')
const password = ref('')
const verifyCode = ref('')
const error = ref('')
const codeSent = ref(false)
const codeSending = ref(false)
const countdown = ref(0)
const devCode = ref('')
const loading = ref(false)

async function sendCode() {
  if (!email.value || !email.value.includes('@')) { error.value = '请输入有效邮箱'; return }
  codeSending.value = true; error.value = ''
  try {
    const { data } = await api.post('/auth/send-code', null, { params: { email: email.value } })
    codeSent.value = true; countdown.value = 60
    if (data.code) { devCode.value = data.code }
    const t = setInterval(() => { countdown.value--; if (countdown.value <= 0) clearInterval(t) }, 1000)
  } catch (e) { error.value = '发送失败' } finally { codeSending.value = false }
}

async function handleRegister() {
  loading.value = true; error.value = ''
  try {
    const { data } = await api.post('/auth/register', {
      email: email.value, password: password.value,
      verify_code: verifyCode.value, nickname: nickname.value || undefined,
    })
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('userName', data.user.nickname || 'User')
    userStore.token = data.access_token; userStore.user = data.user
    router.push('/')
  } catch (e) { error.value = e.response?.data?.detail || '注册失败' } finally { loading.value = false }
}
</script>

<style scoped>
.auth-page { min-height: 80vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
.auth-card { width: 100%; max-width: 420px; background: #fff; border: 1px solid #e7e5e4; border-radius: 16px; padding: 40px 32px; }
.auth-logo { display: flex; align-items: center; gap: 10px; justify-content: center; margin-bottom: 24px; }
.logo-img { width: 40px; height: 40px; border-radius: 8px; }
.auth-logo h1 { font-size: 22px; font-weight: 700; color: #1c1917; }
.auth-card h2 { font-size: 20px; font-weight: 700; color: #0f172a; margin-bottom: 24px; text-align: center; }
.auth-form { display: flex; flex-direction: column; gap: 14px; }
.auth-form label { display: flex; flex-direction: column; gap: 6px; }
.auth-form label span { font-size: 14px; font-weight: 500; color: #475569; }
.auth-form input[type="text"], .auth-form input[type="email"], .auth-form input[type="password"] {
  padding: 12px 14px; border: 1px solid #e7e5e4; border-radius: 10px; font-size: 15px; outline: none;
}
.auth-form input:focus { border-color: #d97706; }
.code-row { display: flex; gap: 8px; }
.code-row input { flex: 1; padding: 12px 14px; border: 1px solid #e7e5e4; border-radius: 10px; font-size: 15px; outline: none; }
.code-row input:focus { border-color: #d97706; }
.btn-code { padding: 12px 16px; background: #f5f5f4; border: 1px solid #e7e5e4; border-radius: 10px; font-size: 13px; color: #78716c; cursor: pointer; white-space: nowrap; }
.btn-code:hover { background: #fef3c7; color: #92400e; }
.btn-code:disabled { opacity: 0.5; cursor: not-allowed; }
.auth-error { font-size: 14px; color: #dc2626; }
.auth-ok { font-size: 14px; color: #16a34a; }
.btn-auth { padding: 12px; background: #d97706; color: #fff; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer; }
.btn-auth:hover { background: #b45309; }
.btn-auth:disabled { opacity: 0.5; cursor: not-allowed; }
.auth-switch { text-align: center; margin-top: 20px; font-size: 14px; color: #a8a29e; }
.auth-switch a { color: #d97706; font-weight: 600; }
</style>
