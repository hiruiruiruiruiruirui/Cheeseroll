// pages/mine/mine.js — User profile & settings
const app = getApp();

Page({
  data: {
    userInfo: null,
    subscriptionStatus: null,
    isLoggedIn: false,
  },

  onShow() {
    this.loadProfile();
  },

  async loadProfile() {
    const token = await app.ensureLogin();
    if (!token) {
      this.setData({ isLoggedIn: false });
      return;
    }

    this.setData({ isLoggedIn: true });

    try {
      // Fetch user profile
      const profileRes = await wx.request({
        url: `${app.globalData.apiBaseUrl}/auth/me`,
        method: 'GET',
        header: { Authorization: `Bearer ${token}` },
      });

      if (profileRes.statusCode === 200) {
        this.setData({ userInfo: profileRes.data });
      }

      // Fetch subscription status
      const subRes = await wx.request({
        url: `${app.globalData.apiBaseUrl}/subscription/status`,
        method: 'GET',
        header: { Authorization: `Bearer ${token}` },
      });

      if (subRes.statusCode === 200) {
        this.setData({ subscriptionStatus: subRes.data });
      }
    } catch (err) {
      console.error('Load profile error:', err);
    }
  },

  // Navigate to various sub-pages
  goTo(e) {
    const page = e.currentTarget.dataset.page;
    wx.navigateTo({ url: page });
  },

  // Handle login
  async handleLogin() {
    const token = await app.ensureLogin();
    if (token) {
      this.loadProfile();
    }
  },

  // Logout
  logout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.globalData.token = null;
          app.globalData.userInfo = null;
          wx.removeStorageSync('token');
          this.setData({ isLoggedIn: false, userInfo: null, subscriptionStatus: null });
          wx.showToast({ title: '已退出', icon: 'success' });
        }
      },
    });
  },

  // Format the subscription info for display
  getSubLabel() {
    const s = this.data.subscriptionStatus;
    if (!s) return '加载中...';
    if (s.has_subscription && s.status === 'active') {
      return `${s.plan_name}（剩余 ${s.remaining_today} 次）`;
    }
    if (s.trial_used) return '试用已用完，点击订阅';
    return '免费试用中（1 次）';
  },
});
