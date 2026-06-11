// pages/index/index.js — Home page with file upload and processing
const app = getApp();

Page({
  data: {
    fileName: '',
    fileId: null,
    isProcessing: false,
    progress: 0,
    statusText: '',
    recentRecords: [],
    pollingTimer: null,
  },

  onShow() {
    this.loadRecentRecords();
  },

  onHide() {
    this.stopPolling();
  },

  // Choose file from chat or album
  async chooseFile() {
    if (this.data.isProcessing) {
      wx.showToast({ title: '正在处理中，请稍候', icon: 'none' });
      return;
    }

    try {
      const res = await wx.chooseMessageFile({
        count: 1,
        type: 'file',
        extension: ['pptx', 'docx', 'pdf'],
      });

      const file = res.tempFiles[0];
      this.setData({ fileName: file.name });
      await this.uploadFile(file);
    } catch (err) {
      if (err.errMsg && err.errMsg.includes('cancel')) return;
      wx.showToast({ title: '选择文件失败', icon: 'none' });
    }
  },

  // Upload file to backend
  async uploadFile(file) {
    const token = await app.ensureLogin();
    if (!token) return;

    wx.showLoading({ title: '上传中...' });

    try {
      const res = await wx.uploadFile({
        url: `${app.globalData.apiBaseUrl}/upload`,
        filePath: file.path,
        name: 'file',
        header: { Authorization: `Bearer ${token}` },
      });

      wx.hideLoading();

      if (res.statusCode === 200) {
        const data = JSON.parse(res.data);
        this.setData({ fileId: data.file_id });
        wx.showToast({ title: '上传成功', icon: 'success' });
        await this.startProcessing();
      } else {
        const data = JSON.parse(res.data);
        wx.showToast({ title: data.detail || '上传失败', icon: 'none' });
      }
    } catch (err) {
      wx.hideLoading();
      wx.showToast({ title: '上传失败，请重试', icon: 'none' });
    }
  },

  // Start AI processing
  async startProcessing() {
    const token = await app.ensureLogin();
    if (!token || !this.data.fileId) return;

    this.setData({
      isProcessing: true,
      progress: 5,
      statusText: '排队中...',
    });

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/process`,
        method: 'POST',
        header: { Authorization: `Bearer ${token}` },
        data: { file_id: this.data.fileId },
      });

      if (res.statusCode === 200) {
        const { task_id } = res.data;
        this.startPolling(task_id);
      } else {
        this.setData({ isProcessing: false });
        wx.showToast({ title: '处理启动失败', icon: 'none' });
      }
    } catch (err) {
      this.setData({ isProcessing: false });
      wx.showToast({ title: '请求失败', icon: 'none' });
    }
  },

  // Poll processing status
  startPolling(taskId) {
    this.stopPolling();

    const progressMap = {
      queued: { progress: 5, text: '排队中...' },
      parsing: { progress: 20, text: '正在解析文档...' },
      generating: { progress: 60, text: 'AI 正在整理笔记...' },
      exporting: { progress: 90, text: '正在生成 PDF...' },
      completed: { progress: 100, text: '完成！' },
      failed: { progress: 0, text: '处理失败' },
    };

    const poll = async () => {
      const token = await app.ensureLogin();
      if (!token) return;

      try {
        const res = await wx.request({
          url: `${app.globalData.apiBaseUrl}/process/${taskId}/status`,
          method: 'GET',
          header: { Authorization: `Bearer ${token}` },
        });

        if (res.statusCode === 200) {
          const { status, progress, record_id, error_message } = res.data;
          const info = progressMap[status] || { progress: 0, text: status };
          this.setData({ progress: info.progress, statusText: info.text });

          if (status === 'completed' && record_id) {
            this.stopPolling();
            wx.showToast({ title: '笔记已生成！', icon: 'success' });
            setTimeout(() => {
              this.setData({ isProcessing: false });
              wx.navigateTo({ url: `/pages/result/result?id=${record_id}` });
            }, 800);
          } else if (status === 'failed') {
            this.stopPolling();
            this.setData({ isProcessing: false });
            wx.showToast({ title: error_message || '处理失败', icon: 'none' });
          }
        }
      } catch (err) {
        console.error('Poll failed:', err);
      }
    };

    this.data.pollingTimer = setInterval(poll, 2000);
    poll(); // Immediate first poll
  },

  stopPolling() {
    if (this.data.pollingTimer) {
      clearInterval(this.data.pollingTimer);
      this.data.pollingTimer = null;
    }
  },

  // Load recent records for preview
  async loadRecentRecords() {
    const token = await app.ensureLogin();
    if (!token) return;

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/records?page=1&page_size=3`,
        method: 'GET',
        header: { Authorization: `Bearer ${token}` },
      });

      if (res.statusCode === 200) {
        const records = res.data.items.map(r => ({
          ...r,
          created_at: this.formatDate(r.created_at),
        }));
        this.setData({ recentRecords: records });
      }
    } catch (err) {
      console.error('Load records failed:', err);
    }
  },

  openRecord(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: `/pages/result/result?id=${id}` });
  },

  formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    const m = d.getMonth() + 1;
    const day = d.getDate();
    const h = d.getHours().toString().padStart(2, '0');
    const min = d.getMinutes().toString().padStart(2, '0');
    return `${m}/${day} ${h}:${min}`;
  },
});
