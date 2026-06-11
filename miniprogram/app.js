// app.js — Mini Program entry
App({
  globalData: {
    userInfo: null,
    token: null,
    apiBaseUrl: 'https://your-api-domain.com/api/v1',
  },

  onLaunch() {
    // Check stored token
    const token = wx.getStorageSync('token');
    if (token) {
      this.globalData.token = token;
    }
  },

  // Get or refresh login
  async ensureLogin() {
    if (this.globalData.token) return this.globalData.token;

    try {
      const { code } = await wx.login();
      const res = await wx.request({
        url: `${this.globalData.apiBaseUrl}/auth/wechat-login`,
        method: 'POST',
        data: { code },
      });

      if (res.statusCode === 200 && res.data.access_token) {
        this.globalData.token = res.data.access_token;
        this.globalData.userInfo = res.data.user;
        wx.setStorageSync('token', res.data.access_token);
        return res.data.access_token;
      }
    } catch (err) {
      console.error('Login failed:', err);
      wx.showToast({ title: '登录失败', icon: 'none' });
    }
    return null;
  },
});
