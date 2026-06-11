// pages/result/result.js — View AI-generated study notes & download PDF
const app = getApp();

Page({
  data: {
    recordId: '',
    record: {},
    loading: true,
    error: '',
    downloading: false,
    markdownNodes: '',
  },

  onLoad(options) {
    if (options.id) {
      this.setData({ recordId: options.id });
      this.loadRecord();
    } else {
      this.setData({ loading: false, error: '缺少笔记 ID' });
    }
  },

  async loadRecord() {
    const token = await app.ensureLogin();
    if (!token) {
      this.setData({ loading: false, error: '请先登录' });
      return;
    }

    this.setData({ loading: true, error: '' });

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/records/${this.data.recordId}`,
        method: 'GET',
        header: { Authorization: `Bearer ${token}` },
      });

      if (res.statusCode === 200) {
        const record = res.data;
        const markdownNodes = this.parseMarkdown(record.original_markdown || '');
        this.setData({
          record,
          markdownNodes,
          loading: false,
        });
      } else {
        this.setData({ loading: false, error: '加载失败' });
      }
    } catch (err) {
      this.setData({ loading: false, error: '网络错误' });
    }
  },

  // Simple Markdown to WXML nodes conversion
  parseMarkdown(md) {
    // Escape HTML
    let html = md
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Headers
    html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

    // Bold and italic
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<em><strong>$1</strong></em>');
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

    // Code blocks
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
    html = html.replace(/`(.+?)`/g, '<code>$1</code>');

    // Tables (simple)
    html = html.replace(/\|(.+)\|/g, (match) => {
      const cells = match.split('|').filter(c => c.trim());
      if (match.includes('---')) return '';
      const cellHtml = cells.map(c => `<td>${c.trim()}</td>`).join('');
      return `<tr>${cellHtml}</tr>`;
    });

    // Lists
    html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
    html = html.replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>');

    // Line breaks and paragraphs
    html = html.replace(/\n\n/g, '<br/><br/>');
    html = html.replace(/\n/g, '<br/>');

    return html;
  },

  // Download PDF
  async downloadPdf() {
    const token = await app.ensureLogin();
    if (!token) return;

    this.setData({ downloading: true });

    try {
      const res = await wx.request({
        url: `${app.globalData.apiBaseUrl}/records/${this.data.recordId}/pdf`,
        method: 'GET',
        header: { Authorization: `Bearer ${token}` },
      });

      if (res.statusCode === 200 && res.data.url) {
        wx.downloadFile({
          url: res.data.url,
          success(result) {
            if (result.statusCode === 200) {
              wx.openDocument({
                filePath: result.tempFilePath,
                fileType: 'pdf',
                success() { wx.showToast({ title: 'PDF 已打开', icon: 'success' }); },
                fail() { wx.showToast({ title: '请安装 PDF 阅读器', icon: 'none' }); },
              });
            }
          },
          fail() {
            wx.showToast({ title: '下载失败', icon: 'none' });
          },
        });
      } else {
        wx.showToast({ title: '获取下载链接失败', icon: 'none' });
      }
    } catch (err) {
      wx.showToast({ title: '请求失败', icon: 'none' });
    } finally {
      this.setData({ downloading: false });
    }
  },

  // Share
  shareRecord() {
    wx.showShareMenu({
      withShareTicket: true,
    });
  },

  onShareAppMessage() {
    const code = this.data.record.share_code || '';
    return {
      title: `复习笔记：${this.data.record.title}`,
      path: code ? `/pages/share/share?code=${code}` : `/pages/result/result?id=${this.data.recordId}`,
    };
  },

  formatDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    return `${d.getFullYear()}/${d.getMonth()+1}/${d.getDate()} ${d.getHours().toString().padStart(2,'0')}:${d.getMinutes().toString().padStart(2,'0')}`;
  },
});
