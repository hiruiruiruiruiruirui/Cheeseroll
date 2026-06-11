<template>
  <div id="app">
    <header class="app-header" v-if="showNav">
      <div class="header-content">
        <router-link to="/" class="logo">
          <img src="/logo.png" alt="芝士卷" class="logo-img" />
          <span class="logo-text">芝士卷</span>
          <span class="logo-sub">Cheese Roll</span>
        </router-link>
        <nav class="nav-links">
          <router-link to="/">{{ T.nav.home }}</router-link>
          <router-link to="/history">{{ T.nav.notes }}</router-link>
          <router-link to="/wrong-answers">{{ T.nav.wrong }}</router-link>
          <router-link to="/plans">{{ T.nav.plans }}</router-link>
          <router-link to="/mine">{{ T.nav.mine }}</router-link>
        </nav>
        <div class="header-right">
          <template v-if="isLoggedIn">
            <router-link to="/mine" class="user-chip">
              <span class="user-avatar">🧀</span>
              <span class="user-name">{{ userName }}</span>
            </router-link>
          </template>
          <template v-else>
            <router-link to="/login" class="nav-auth-link">登录</router-link>
            <router-link to="/register" class="btn btn-sm btn-primary">注册</router-link>
          </template>
          <select class="lang-switch" v-model="currentLang" @change="switchLang">
            <option v-for="l in availableLocales" :key="l.code" :value="l.code">{{ l.label }}</option>
          </select>
        </div>
      </div>
    </header>
    <main :class="{ 'has-nav': showNav }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { t, locale, setLocale, availableLocales } from './utils/i18n'

const route = useRoute()
const showNav = computed(() => !route.path.startsWith('/share/'))
const T = computed(() => t.value)
const currentLang = ref(locale.value)
const isLoggedIn = ref(!!localStorage.getItem('token'))
const userName = ref(localStorage.getItem('userName') || 'User')

watch(() => route.path, () => {
  isLoggedIn.value = !!localStorage.getItem('token')
  userName.value = localStorage.getItem('userName') || 'User'
})

function switchLang() {
  setLocale(currentLang.value)
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  font-size: 15px;
  color: #292524;
  background: #fafaf9;
  line-height: 1.6;
}
a { text-decoration: none; color: inherit; }

:root {
  --cheese-gold: #E8A317;
  --cheese-bright: #F5A623;
  --cheese-light: #FFF3D6;
  --dark: #1E1E1E;
  --mid-gray: #4A4A4A;
  --muted: #8B8B8B;
  --bg: #FAF8F5;
  --card: #FFFFFF;
  --border: #EBE7E0;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e7e5e4;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  gap: 24px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  cursor: pointer;
  flex-shrink: 0;
}
.logo-img { width: 36px; height: 36px; border-radius: 8px; }
.logo-icon { font-size: 28px; }
.logo-text {
  font-size: 20px;
  color: #1c1917;
  letter-spacing: 1px;
}
.logo-sub {
  font-size: 11px;
  color: #a8a29e;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-left: 4px;
  padding-top: 2px;
}
.nav-links {
  display: flex;
  gap: 24px;
}
.nav-links a {
  font-size: 14px;
  color: #78716c;
  font-weight: 500;
  transition: color 0.2s;
  padding: 4px 0;
  border-bottom: 2px solid transparent;
  white-space: nowrap;
}
.nav-links a:hover,
.nav-links a.router-link-active {
  color: #d97706;
  border-bottom-color: #d97706;
}
.header-right { flex-shrink: 0; display: flex; align-items: center; gap: 12px; }
.xp-display { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.xp-level { font-weight: 700; color: #d97706; white-space: nowrap; }
.xp-bar-wrap { width: 48px; height: 4px; background: #e7e5e4; border-radius: 2px; overflow: hidden; }
.xp-bar-fill { height: 100%; background: #d97706; border-radius: 2px; transition: width 0.5s; }
.nav-auth-link { font-size: 14px; color: #78716c; font-weight: 500; }
.nav-auth-link:hover { color: #d97706; }
.user-chip { display: flex; align-items: center; gap: 6px; font-size: 14px; color: #475569; font-weight: 500; }
.user-avatar { font-size: 18px; }
.lang-switch {
  font-size: 13px;
  padding: 6px 10px;
  border: 1px solid #e7e5e4;
  border-radius: 8px;
  background: #fff;
  color: #78716c;
  cursor: pointer;
  outline: none;
}
.lang-switch:focus { border-color: #d97706; }

main { min-height: calc(100vh - 60px); }
main.has-nav { padding-top: 0; }

/* Shared styles */
.container { max-width: 900px; margin: 0 auto; padding: 24px; }
.card {
  background: #fff;
  border-radius: 14px;
  padding: 24px;
  margin-bottom: 16px;
  border: 1px solid #e7e5e4;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary { background: #d97706; color: #fff; }
.btn-primary:hover { background: #b45309; }
.btn-primary:disabled { background: #e7c897; cursor: not-allowed; }
.btn-outline { background: transparent; color: #d97706; border: 2px solid #d97706; }
.btn-outline:hover { background: #fffbeb; }
.btn-sm { padding: 6px 16px; font-size: 13px; border-radius: 8px; }
.text-muted { color: #a8a29e; }
.text-sm { font-size: 13px; }
.mt-16 { margin-top: 16px; }
.mb-16 { margin-bottom: 16px; }
.flex { display: flex; }
.flex-between { display: flex; align-items: center; justify-content: space-between; }

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #fafaf9; }
::-webkit-scrollbar-thumb { background: #d4cfc4; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #b0aba0; }

@media (max-width: 768px) {
  .header-content { padding: 0 12px; }
  .nav-links { gap: 12px; }
  .nav-links a { font-size: 13px; }
  .lang-switch { font-size: 12px; padding: 4px 6px; }
}
</style>
