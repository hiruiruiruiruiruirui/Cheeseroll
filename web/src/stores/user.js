// stores/user.js — Pinia store for user auth state
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)

  const isLoggedIn = computed(() => !!token.value)

  async function wechatLogin(code) {
    const { data } = await api.post('/auth/wechat-login', { code })
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('token', data.access_token)
    return data
  }

  async function fetchProfile() {
    if (!token.value) return
    const { data } = await api.get('/auth/me')
    user.value = data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return { user, token, isLoggedIn, wechatLogin, fetchProfile, logout }
})
