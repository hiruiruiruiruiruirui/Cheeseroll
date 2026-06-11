// pages/plans/plans.js — Subscription plans page with WeChat Pay
const app = getApp();
const { PLANS } = require('../../utils/constants');
const { request } = require('../../utils/api');

Page({
  data: {
    plans: PLANS,
    currentPlan: null,        // User's active plan type
    subscriptionStatus: null,  // Full status from API
    loading: false,
    subscribingPlan: null,     // Plan being paid for
  },

  onShow() {
    this.loadSubscriptionStatus();
  },

  // Fetch current subscription status
  async loadSubscriptionStatus() {
    const token = await app.ensureLogin();
    if (!token) return;

    this.setData({ loading: true });

    try {
      const data = await request({
        url: '/subscription/status',
        method: 'GET',
      });

      this.setData({
        subscriptionStatus: data,
        currentPlan: data.has_subscription ? data.plan_type : null,
        loading: false,
      });
    } catch (err) {
      console.error('Load subscription status failed:', err);
      this.setData({ loading: false });
    }
  },

  // Subscribe to a plan
  async subscribe(e) {
    const planType = e.currentTarget.dataset.type;
    const plan = this.data.plans.find(p => p.type === planType);
    if (!plan) return;

    // If already on this plan, skip
    if (this.data.currentPlan === planType && this.data.subscriptionStatus?.status === 'active') {
      wx.showToast({ title: '您已订阅此方案', icon: 'none' });
      return;
    }

    const token = await app.ensureLogin();
    if (!token) return;

    this.setData({ subscribingPlan: planType });

    try {
      // Step 1: Create payment order
      wx.showLoading({ title: '创建订单...' });

      const orderData = await request({
        url: '/payment/order',
        method: 'POST',
        data: { plan_type: planType },
      });

      wx.hideLoading();

      if (!orderData.wx_pay_params) {
        wx.showToast({ title: '支付服务暂不可用', icon: 'none' });
        this.setData({ subscribingPlan: null });
        return;
      }

      // Step 2: Invoke WeChat Pay
      const payParams = orderData.wx_pay_params;

      wx.requestPayment({
        timeStamp: payParams.timeStamp,
        nonceStr: payParams.nonceStr,
        package: payParams.package,
        signType: payParams.signType || 'RSA',
        paySign: payParams.paySign,
        success: () => {
          wx.showToast({ title: '支付成功！', icon: 'success' });
          // Refresh subscription status
          setTimeout(() => {
            this.loadSubscriptionStatus();
            this.setData({ subscribingPlan: null });
          }, 1500);
        },
        fail: (err) => {
          console.error('Payment failed:', err);
          if (err.errMsg && err.errMsg.includes('cancel')) {
            wx.showToast({ title: '已取消支付', icon: 'none' });
          } else {
            wx.showToast({ title: '支付失败，请重试', icon: 'none' });
          }
          this.setData({ subscribingPlan: null });
        },
      });
    } catch (err) {
      wx.hideLoading();
      console.error('Subscribe error:', err);
      wx.showToast({ title: err.message || '创建订单失败', icon: 'none' });
      this.setData({ subscribingPlan: null });
    }
  },

  // Check if a plan is the user's current active plan
  isCurrentPlan(planType) {
    return this.data.currentPlan === planType &&
           this.data.subscriptionStatus?.status === 'active';
  },
});
