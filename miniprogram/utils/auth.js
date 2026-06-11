// utils/auth.js — WeChat login flow

const app = getApp();

/**
 * Ensure user is logged in. Returns a valid token.
 * Uses wx.login() to get a code, exchanges it for JWT.
 */
async function ensureLogin() {
  if (app.globalData.token) {
    return app.globalData.token;
  }

  try {
    const loginRes = await new Promise((resolve, reject) => {
      wx.login({
        success: resolve,
        fail: reject,
      });
    });

    const res = await new Promise((resolve, reject) => {
      wx.request({
        url: `${app.globalData.apiBaseUrl}/auth/wechat-login`,
        method: 'POST',
        data: { code: loginRes.code },
        success: resolve,
        fail: reject,
      });
    });

    if (res.statusCode === 200 && res.data.access_token) {
      app.globalData.token = res.data.access_token;
      app.globalData.userInfo = res.data.user;
      wx.setStorageSync('token', res.data.access_token);
      return res.data.access_token;
    }

    throw new Error('Login failed');
  } catch (err) {
    console.error('Login error:', err);
    wx.showToast({ title: '登录失败，请重启小程序', icon: 'none' });
    return null;
  }
}

/**
 * Check if user is logged in.
 */
function isLoggedIn() {
  return !!app.globalData.token;
}

/**
 * Clear login state.
 */
function logout() {
  app.globalData.token = null;
  app.globalData.userInfo = null;
  wx.removeStorageSync('token');
}

module.exports = { ensureLogin, isLoggedIn, logout };
