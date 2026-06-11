// pages/share/share.js — Public shared note view (no login required)
const app = getApp();

Page({
  data: {
    shareCode: '',
    record: null,
    loading: true,
    error: '',
    markdownNodes: '',
  },

  onLoad(options) {
    if (options.code) {
      this.setData({ shareCode: options.code });
      this.loadSharedNote();
    } else if (options.scene) {
      // Deferred deep link: scene parameter from WeChat (e.g. scanned QR code)
      const code = decodeURIComponent(options.scene);
      this.setData({ shareCode: code });
      this.loadSharedNote();
    } else {
      this.setData({ loading: false, error: '笔记分享码缺失' });
    }
  },

  async loadSharedNote() {
    this.setData({ loading: true, error: '' });

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/share/${this.data.shareCode}`,
        method: 'GET',
      });

      if (res.statusCode === 200) {
        const record = res.data;
        const markdownNodes = this.parseMarkdown(record.original_markdown || '');
        this.setData({ record, markdownNodes, loading: false });
      } else {
        this.setData({
          loading: false,
          error: res.data?.detail || '笔记不存在或已删除',
        });
      }
    } catch (err) {
      this.setData({ loading: false, error: '网络连接失败' });
    }
  },

  // Simple Markdown → HTML (shared with result page)
  parseMarkdown(md) {
    if (!md) return '';
    let html = md
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    html = html.replace(/`(.+?)`/g, '<code>$1</code>');
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/\n\n/g, '<br/><br/>');
    html = html.replace(/\n/g, '<br/>');

    return html;
  },

  // Open the Mini Program from share page (navigate to home)
  goToApp() {
    wx.switchTab({ url: '/pages/index/index' });
  },

  // Share this note to others
  onShareAppMessage() {
    return {
      title: `复习笔记：${this.data.record?.title || '学习笔记'}`,
      path: `/pages/share/share?code=${this.data.shareCode}`,
      imageUrl: '',  // TODO: generate share image via Canvas
    };
  },
});
