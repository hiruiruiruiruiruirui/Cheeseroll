// utils/api.js — wx.request wrapper with auth token injection

const app = getApp();

/**
 * Make an authenticated API request.
 * Automatically injects the Bearer token and retries on 401.
 */
function request(options) {
  return new Promise((resolve, reject) => {
    const token = app.globalData.token;
    const header = {
      'Content-Type': 'application/json',
      ...options.header,
    };

    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }

    wx.request({
      url: `${app.globalData.apiBaseUrl}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header,
      success(res) {
        if (res.statusCode === 401) {
          // Token expired — clear and let caller re-login
          app.globalData.token = null;
          wx.removeStorageSync('token');
          reject(new Error('Unauthorized'));
        } else if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(new Error(res.data?.detail || `HTTP ${res.statusCode}`));
        }
      },
      fail(err) {
        reject(new Error(err.errMsg || 'Network error'));
      },
    });
  });
}

module.exports = { request };
