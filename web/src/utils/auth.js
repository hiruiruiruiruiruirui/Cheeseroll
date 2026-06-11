// utils/auth.js — Web auth helpers (QR code login placeholder)

import api from './api'

/**
 * Initialize WeChat QR login.
 * In production, embeds the official WeChat OAuth QR code iframe.
 * For dev, returns a mock login function.
 */
export async function initQrLogin(containerId) {
  const container = document.getElementById(containerId)
  if (!container) return

  // In production: redirect to WeChat OAuth URL
  // const redirectUri = encodeURIComponent(window.location.origin + '/auth/callback')
  // const qrUrl = `https://open.weixin.qq.com/connect/qrconnect?appid=${APPID}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_login&state=STATE#wechat_redirect`

  container.innerHTML = `
    <div style="text-align:center;padding:24px;color:#888;">
      <p>请使用微信扫描二维码登录</p>
      <div style="width:200px;height:200px;background:#f0f0f0;margin:16px auto;display:flex;align-items:center;justify-content:center;">
        [微信扫码登录]
      </div>
      <p class="text-sm">需在微信开放平台配置网站应用</p>
    </div>
  `
}

/**
 * Check if user has a valid token.
 */
export function isAuthenticated() {
  return !!localStorage.getItem('token')
}

/**
 * Get the stored token.
 */
export function getToken() {
  return localStorage.getItem('token')
}
