// pages/history/history.js — Study records history
const app = getApp();

Page({
  data: {
    records: [],
    loading: true,
    page: 1,
    total: 0,
    pageSize: 20,
    hasMore: false,
  },

  onShow() {
    this.setData({ page: 1, records: [] });
    this.loadRecords();
  },

  onReachBottom() {
    if (this.data.hasMore) {
      this.setData({ page: this.data.page + 1 });
      this.loadRecords();
    }
  },

  onPullDownRefresh() {
    this.setData({ page: 1, records: [] });
    this.loadRecords().then(() => wx.stopPullDownRefresh());
  },

  async loadRecords() {
    const token = await app.ensureLogin();
    if (!token) {
      this.setData({ loading: false });
      return;
    }

    this.setData({ loading: this.data.page === 1 });

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/records`,
        method: 'GET',
        data: { page: this.data.page, page_size: this.data.pageSize },
        header: { Authorization: `Bearer ${token}` },
      });

      if (res.statusCode === 200) {
        const items = (res.data.items || []).map(r => ({
          ...r,
          created_at: this.formatDate(r.created_at),
          statusText: this.statusLabel(r.status),
        }));

        this.setData({
          records: this.data.page === 1 ? items : [...this.data.records, ...items],
          total: res.data.total,
          hasMore: this.data.records.length + items.length < res.data.total,
          loading: false,
        });
      }
    } catch (err) {
      console.error('Load records error:', err);
      this.setData({ loading: false });
    }
  },

  openRecord(e) {
    const id = e.currentTarget.dataset.id;
    const status = e.currentTarget.dataset.status;
    if (status === 'completed') {
      wx.navigateTo({ url: `/pages/result/result?id=${id}` });
    } else if (status === 'processing') {
      wx.showToast({ title: '笔记还在生成中...', icon: 'none' });
    } else {
      wx.showToast({ title: '此笔记生成失败', icon: 'none' });
    }
  },

  statusLabel(status) {
    const map = { completed: '✅ 已完成', processing: '⏳ 处理中', failed: '❌ 失败', queued: '🕐 排队中' };
    return map[status] || status;
  },

  formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const y = d.getFullYear();
    const m = (d.getMonth() + 1).toString().padStart(2, '0');
    const day = d.getDate().toString().padStart(2, '0');
    const h = d.getHours().toString().padStart(2, '0');
    const min = d.getMinutes().toString().padStart(2, '0');
    return `${y}/${m}/${day} ${h}:${min}`;
  },
});
